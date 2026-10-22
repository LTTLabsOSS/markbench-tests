"""UL Procyon Computer Vision test script"""

import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from procyon_ai_utils import (
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
    get_openvino_devices,
    get_openvino_gpu,
    get_winml_devices,
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
    "AMD_CPU",
    "AMD_GPU0",
    "AMD_GPU1",
    "Intel_CPU",
    "Intel_GPU0",
    "Intel_GPU1",
    "Intel_NPU",
    "NVIDIA_GPU",
    "Qualcomm_HTP",
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


#need to clean this up and test for different configs
def get_benchmark_config(engine):
    if engine == "AMD_CPU":
        winml_devices = get_winml_devices(ABS_EXECUTABLE_PATH)
        device_name = winml_devices.get("CPU")

        if device_name is None:
            raise RuntimeError(
                "WinML did not detect a CPU device."
            )

        return {
            "config": f'"{CONFIG_DIR}\\ai_computer_vision_winml_cpu.def"',
            "process_name": "WinML.exe",
            "device_name": device_name,
            "device_id": "CPU",
            "test_name": "cpu_float32",
            "api": "winml",
        }

    if engine in ("AMD_GPU0", "AMD_GPU1"):
        winml_devices = get_winml_devices(ABS_EXECUTABLE_PATH)
        devices = list(winml_devices.items())

        if not devices:
            raise RuntimeError(
                "No WinML GPU devices were detected, but an AMD GPU test was requested."
            )

        if engine == "AMD_GPU0":
            device_index = 0
        else:
            device_index = 1 if len(devices) > 1 else 0

        device_id, device_name = devices[device_index]

        return {
            "config": f'"{CONFIG_DIR}\\ai_computer_vision_winml_gpu.def"',
            "process_name": "WinML.exe",
            "device_name": device_name,
            "device_id": device_id,
            "test_name": "gpu_float32",
            "api": "winml",
        }

    if engine == "Intel_CPU":
        openvino_devices = get_openvino_devices(ABS_EXECUTABLE_PATH)
        device_name = openvino_devices.get("CPU")

        if device_name is None:
            raise RuntimeError(
                "OpenVINO did not detect a CPU device."
            )

        return {
            "config": f'"{CONFIG_DIR}\\ai_computer_vision_openvino_cpu.def"',
            "process_name": "OpenVino.exe",
            "device_id": "CPU",
            "device_name": device_name,
            "test_name": "cpu_float32",
            "api": "openvino",
        }

    if engine in ("Intel_GPU0", "Intel_GPU1", "Intel_NPU"):
        openvino_devices = get_openvino_devices(ABS_EXECUTABLE_PATH)

        if engine == "Intel_NPU":
            device_id = "NPU"
            device_name = openvino_devices.get("NPU")

            if device_name is None:
                raise RuntimeError(
                    "OpenVINO did not detect an NPU device."
                )

            config = f'"{CONFIG_DIR}\\ai_computer_vision_openvino_npu.def"'
            test_name = "npu_float32"

        else:
            requested_gpu = "GPU.0" if engine == "Intel_GPU0" else "GPU.1"

            if requested_gpu in openvino_devices:
                device_id = requested_gpu
            elif "GPU" in openvino_devices:
                device_id = "GPU"
            else:
                raise RuntimeError(
                    "OpenVINO did not detect a GPU device."
                )

            device_name = get_openvino_gpu(openvino_devices, requested_gpu)
            config = f'"{CONFIG_DIR}\\ai_computer_vision_openvino_gpu.def"'
            test_name = "gpu_float32"

        return {
            "config": config,
            "process_name": "OpenVino.exe",
            "device_id": device_id,
            "device_name": device_name,
            "test_name": test_name,
            "api": "openvino",
        }

    if engine == "NVIDIA_GPU":
        cuda_devices = get_cuda_devices(ABS_EXECUTABLE_PATH)

        device_id = "cuda:0"

        if device_id not in cuda_devices:
            raise RuntimeError(
                "CUDA device cuda:0 was not detected."
            )

        return {
            "config": f'"{CONFIG_DIR}\\ai_computer_vision_tensorrt.def"',
            "device_id": device_id,
            "device_name": cuda_devices[device_id],
            "process_name": "TensorRT.exe",
            "test_name": "gpu_float32",
            "api": "tensorrt",
        }

#need to potentially adjust the device id and name here
    if engine == "Qualcomm_HTP":
        return {
            "config": f'"{CONFIG_DIR}\\ai_computer_vision_snpe.def"',
            "device_id": "CPU",
            "device_name": "CPU",
            "process_name": "SNPE.exe",
            "test_name": "htp_integer",
            "api": "snpe",
        }

    raise ValueError(f"Unsupported benchmark engine: {engine}")


def create_procyon_command(test_option, process_name, device_id):
    """create command string"""
    command = ""

    if device_id == "CPU":
        command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}"'
    else:
        match process_name:
            case "WinML.exe":
                command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-winml-device {device_id}'
            case "OpenVino.exe":
                command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-openvino-device {device_id}'
            case "TensorRT.exe":
                command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-cuda-device {device_id}'
    command = command.rstrip()
    return command


def run_benchmark(process_name, command_to_run):
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
        logger.info("Procyon AI Computer Vision benchmark has started.")
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
    pr = run_benchmark(benchmark_config["process_name"], cmd)

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
        "test": "Procyon AI CV",
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
