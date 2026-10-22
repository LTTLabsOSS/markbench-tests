"""UL Procyon AI Image Generation test script"""

import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from procyon_ai_img_gen_utils import (
    check_procyon_run_status,
    find_procyon_versions,
    find_score_in_xml,
    find_test_version,
    get_install_path,
    is_process_running,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import create_artifacts_manifest
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.report import seconds_to_milliseconds, write_report_json
from non_games.procyon.procyoncmd import (
    get_cuda_devices,
    get_directml_devices,
    get_openvino_devices,
    get_openvino_gpu,
)

logger = logging.getLogger(__name__)

#####
# Globals
#####
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)

DIR_PROCYON = Path(get_install_path())
EXECUTABLE = "ProcyonCmd.exe"
ABS_EXECUTABLE_PATH = DIR_PROCYON / EXECUTABLE

CONFIG_DIR = SCRIPT_DIRECTORY / "config"
BENCHMARK_ENGINES = (
    "AMD_GPU0_FP16",
    "AMD_GPU1_FP16",
    "AMD_GPU0_XL_FP16",
    "AMD_GPU1_XL_FP16",
    "Intel_GPU0_INT8",
    "Intel_GPU0_FP16",
    "Intel_GPU0_XL_FP16",
    "Intel_GPU1_INT8",
    "Intel_GPU1_FP16",
    "Intel_GPU1_XL_FP16",
    "NVIDIA_GPU_INT8",
    "NVIDIA_GPU_FP16",
    "NVIDIA_GPU_XL_FP16",
)

RESULTS_FILENAME = "result.xml"
RESULTS_XML_PATH = ARTIFACTS_DIRECTORY / RESULTS_FILENAME
PROCYON_LOG_PATH = ARTIFACTS_DIRECTORY / "procyon_log.txt"


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine",
        dest="engine",
        help="Engine test type",
        required=True,
        choices=BENCHMARK_ENGINES,
    )
    argies = parser.parse_args()
    return argies


#probably need to clean this up some.
def get_benchmark_config(engine):
    """Get benchmark configuration and select the appropriate device."""

    if engine in (
        "AMD_GPU0_FP16",
        "AMD_GPU1_FP16",
        "AMD_GPU0_XL_FP16",
        "AMD_GPU1_XL_FP16",
    ):
        directml_devices = get_directml_devices(ABS_EXECUTABLE_PATH)
        devices = list(directml_devices.items())

        gpu_devices = [
            (device_id, device_name)
            for device_id, device_name in devices
            if "CPU" not in device_name.upper()
        ]

        if not gpu_devices:
            raise RuntimeError(
                "No DirectML GPU devices were detected, "
                "but an AMD GPU test was requested."
            )

        if engine in ("AMD_GPU0_FP16", "AMD_GPU0_XL_FP16"):
            device_index = 0
        else:
            if len(gpu_devices) < 2:
                raise RuntimeError(
                    "A second DirectML GPU was not detected."
                )
            device_index = 1

        device_id, device_name = gpu_devices[device_index]

        if engine in ("AMD_GPU0_FP16", "AMD_GPU1_FP16"):
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sd15fp16_onnxruntime.def"'
            )
            test_name = "stable_diffusion_fp16"

        else:
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sdxlfp16_onnxruntime.def"'
            )
            test_name = "stable_diffusion_fp16_xl"

        return {
            "config": config,
            "process_name": "ort-directml.exe",
            "device_name": device_name,
            "device_id": device_id,
            "test_name": test_name,
            "api": "onnx",
        }

    if engine in (
        "Intel_GPU0_INT8",
        "Intel_GPU0_FP16",
        "Intel_GPU0_XL_FP16",
        "Intel_GPU1_INT8",
        "Intel_GPU1_FP16",
        "Intel_GPU1_XL_FP16",
    ):
        openvino_devices = get_openvino_devices(ABS_EXECUTABLE_PATH)

        if engine in (
            "Intel_GPU0_INT8",
            "Intel_GPU0_FP16",
            "Intel_GPU0_XL_FP16",
        ):
            requested_gpu = "GPU.0"
        else:
            requested_gpu = "GPU.1"

        if requested_gpu in openvino_devices:
            device_id = requested_gpu
        elif "GPU" in openvino_devices:
            device_id = "GPU"
        else:
            raise RuntimeError(
                f"OpenVINO did not detect {requested_gpu}."
            )

        device_name = get_openvino_gpu(
            openvino_devices,
            requested_gpu,
        )

        if engine in ("Intel_GPU0_INT8", "Intel_GPU1_INT8"):
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sd15int8_openvino.def"'
            )
            test_name = "stable_diffusion_int8"

        elif engine in ("Intel_GPU0_FP16", "Intel_GPU1_FP16"):
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sd15fp16_openvino.def"'
            )
            test_name = "stable_diffusion_fp16"

        else:
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sdxlfp16_openvino.def"'
            )
            test_name = "stable_diffusion_fp16_xl"

        return {
            "config": config,
            "process_name": "openvino.exe",
            "device_id": device_id,
            "device_name": device_name,
            "test_name": test_name,
            "api": "openvino",
        }

    if engine in (
        "NVIDIA_GPU_INT8",
        "NVIDIA_GPU_FP16",
        "NVIDIA_GPU_XL_FP16",
    ):
        cuda_devices = get_cuda_devices(ABS_EXECUTABLE_PATH)

        device_id = "cuda:0"
        device_name = cuda_devices.get(device_id)

        if device_name is None:
            raise RuntimeError(
                "CUDA device cuda:0 was not detected."
            )

        if engine == "NVIDIA_GPU_INT8":
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sd15int8_tensorrt.def"'
            )
            test_name = "stable_diffusion_int8"

        elif engine == "NVIDIA_GPU_FP16":
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sd15fp16_tensorrt.def"'
            )
            test_name = "stable_diffusion_fp16"

        else:
            config = (
                f'"{CONFIG_DIR}\\'
                'ai_imagegeneration_sdxlfp16_tensorrt.def"'
            )
            test_name = "stable_diffusion_fp16_xl"

        return {
            "config": config,
            "process_name": "tensorrt.exe",
            "device_id": device_id,
            "device_name": device_name,
            "test_name": test_name,
            "api": "tensorrt",
        }

    raise ValueError(f"Unsupported benchmark engine: {engine}")


def create_procyon_command(test_option, process_name, device_id):
    """create command string"""
    command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}"'

    match process_name:
        case "ort-directml.exe":
            command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-directml-device {device_id}'
        case "openvino.exe":
            command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-openvino-device {device_id}'
        case "tensorrt.exe":
            command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-cuda-device {device_id}'
    command = command.rstrip()

    return command


def run_benchmark(process_name, command_to_run, start_time):
    """run the benchmark"""
    with (
        open(
            PROCYON_LOG_PATH,
            "w",
            encoding="utf-8",
            errors="replace",
        ) as console_log,
        subprocess.Popen(
            command_to_run,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        ) as proc,
    ):
        logger.info("Procyon AI Image Generation benchmark has started.")
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 60:  # seconds
                raise ValueError("BenchMark subprocess did not start in time")
            process = is_process_running(process_name)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)

        for line in proc.stdout:
            line = line.rstrip("\r\n")
            console_log.write(line + "\n")
            console_log.flush()
                
        proc.wait()
        return proc


try:
    setup_logging(LOG_DIRECTORY)

    args = get_arguments()
    logger.info("Requested benchmark engine: %s", args.engine)

    benchmark_config = get_benchmark_config(args.engine)

    logger.info(
        "Selected device: %s",
        benchmark_config["device_name"],
    )
    
    logger.info(
        "Selected device ID: %s", 
        benchmark_config["device_id"], 
    )

    logger.info(
        "Selected API: %s",
        benchmark_config["api"],
    )

    option = benchmark_config["config"]
    proc_name = benchmark_config["process_name"]
    dev_id = benchmark_config["device_id"]
    test_version = find_test_version()
    cmd = create_procyon_command(option, proc_name, dev_id)
    logger.info("Starting benchmark!")
    logger.info(cmd)
    start_time = time.time()
    pr = run_benchmark(proc_name, cmd, start_time)

    if pr.returncode > 0:
        logger.error("Procyon exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    if not check_procyon_run_status(PROCYON_LOG_PATH):
        logger.error("Procyon reported that the run ended with an error.")
        sys.exit(1)

    procyon_client_version, procyon_product_version = find_procyon_versions(
        PROCYON_LOG_PATH
    )

    if procyon_product_version is None:
        logger.warning("Could not determine Procyon Product Version.")

    if procyon_client_version is None:
        logger.warning("Could not determine Procyon Client Version.")

    logger.info("Procyon Client Version: %s", procyon_client_version)
    logger.info("Procyon Product Version: %s", procyon_product_version)

    score = find_score_in_xml()

    if score is None:
        logger.error("Could not find overall score!")
        sys.exit(1)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)
    logger.info("Benchmark took %.2f seconds", elapsed_test_time)
    logger.info("Score was %s", score)

    report = {
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "test": "Procyon AI Image Generation",
        "test_parameter": benchmark_config["test_name"],
        "api": benchmark_config["api"],
        "test_version": test_version,
        "device_name": benchmark_config["device_name"],
        "procyon_client_version": procyon_client_version,
        "procyon_product_version": procyon_product_version,
        "unit": "score",
        "score": score,
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    sys.exit(1)
