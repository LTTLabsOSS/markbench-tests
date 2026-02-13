"""UL Procyon AI Image Generation test script"""

# pylint: disable=no-name-in-module
import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from procyon_ai_img_gen_utils import (
    find_procyon_version,
    find_score_in_xml,
    find_test_version,
    get_install_path,
    is_process_running,
)

PARENT_DIR = str(Path(sys.path[0], "../.."))
sys.path.append(PARENT_DIR)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.procyoncmd import (
    get_cuda_devices,
    get_openvino_devices,
    get_openvino_gpu,
    get_winml_devices,
)

#####
# Globals
#####
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
DIR_PROCYON = Path(get_install_path())
EXECUTABLE = "ProcyonCmd.exe"
ABS_EXECUTABLE_PATH = DIR_PROCYON / EXECUTABLE
WINML_DEVICES = get_winml_devices(ABS_EXECUTABLE_PATH)
OPENVINO_DEVICES = get_openvino_devices(ABS_EXECUTABLE_PATH)
CUDA_DEVICES = get_cuda_devices(ABS_EXECUTABLE_PATH)

CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "AMD_GPU0_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_onnxruntime.def"',
        "process_name": "ort-directml.exe",
        "device_name": list(WINML_DEVICES.keys())[0],
        "device_id": "0",
        "test_name": "stable_diffusion_fp16",
        "api": "onnx",
    },
    "AMD_GPU1_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_onnxruntime.def"',
        "process_name": "ort-directml.exe",
        "device_name": list(WINML_DEVICES.keys())[1]
        if len(list(WINML_DEVICES.keys())) > 1
        else list(WINML_DEVICES.keys())[0],
        "device_id": "1" if len(list(WINML_DEVICES.values())) > 1 else "0",
        "test_name": "stable_diffusion_fp16",
        "api": "onnx",
    },
    "AMD_GPU0_XL_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_onnxruntime.def"',
        "process_name": "ort-directml.exe",
        "device_name": list(WINML_DEVICES.keys())[0],
        "device_id": "0",
        "test_name": "stable_diffusion_fp16_xl",
        "api": "onnx",
    },
    "AMD_GPU1_XL_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_onnxruntime.def"',
        "process_name": "ort-directml.exe",
        "device_name": list(WINML_DEVICES.keys())[1]
        if len(list(WINML_DEVICES.keys())) > 1
        else list(WINML_DEVICES.keys())[0],
        "device_id": list(WINML_DEVICES.values())[1]
        if len(list(WINML_DEVICES.values())) > 1
        else list(WINML_DEVICES.values())[0],
        "test_name": "stable_diffusion_fp16_xl",
        "api": "onnx",
    },
    "Intel_GPU0_INT8": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15int8_openvino.def"',
        "process_name": "openvino.exe",
        "device_id": "GPU.0" if "GPU.0" in list(OPENVINO_DEVICES.keys()) else "GPU",
        "device_name": get_openvino_gpu(OPENVINO_DEVICES, "GPU.0"),
        "test_name": "stable_diffusion_int8",
        "api": "openvino",
    },
    "Intel_GPU0_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_openvino.def"',
        "process_name": "openvino.exe",
        "device_id": "GPU.0" if "GPU.0" in list(OPENVINO_DEVICES.keys()) else "GPU",
        "device_name": get_openvino_gpu(OPENVINO_DEVICES, "GPU.0"),
        "test_name": "stable_diffusion_fp16",
        "api": "openvino",
    },
    "Intel_GPU0_XL_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_openvino.def"',
        "process_name": "openvino.exe",
        "device_id": "GPU.0" if "GPU.0" in list(OPENVINO_DEVICES.keys()) else "GPU",
        "device_name": get_openvino_gpu(OPENVINO_DEVICES, "GPU.0"),
        "test_name": "stable_diffusion_fp16_xl",
        "api": "openvino",
    },
    "Intel_GPU1_INT8": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15int8_openvino.def"',
        "process_name": "openvino.exe",
        "device_id": "GPU.1" if "GPU.1" in list(OPENVINO_DEVICES.keys()) else "GPU",
        "device_name": get_openvino_gpu(OPENVINO_DEVICES, "GPU.1"),
        "test_name": "stable_diffusion_int8",
        "api": "openvino",
    },
    "Intel_GPU1_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_openvino.def"',
        "process_name": "openvino.exe",
        "device_id": "GPU.1" if "GPU.1" in list(OPENVINO_DEVICES.keys()) else "GPU",
        "device_name": get_openvino_gpu(OPENVINO_DEVICES, "GPU.1"),
        "test_name": "stable_diffusion_fp16",
        "api": "openvino",
    },
    "Intel_GPU1_XL_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_openvino.def"',
        "process_name": "openvino.exe",
        "device_id": "GPU.1" if "GPU.1" in list(OPENVINO_DEVICES.keys()) else "GPU",
        "device_name": get_openvino_gpu(OPENVINO_DEVICES, "GPU.1"),
        "test_name": "stable_diffusion_fp16_xl",
        "api": "openvino",
    },
    "NVIDIA_GPU_INT8": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15int8_tensorrt.def"',
        "process_name": "tensorrt.exe",
        "device_id": "cuda:0",
        "device_name": CUDA_DEVICES.get("cuda:0"),
        "test_name": "stable_diffusion_int8",
        "api": "tensorrt",
    },
    "NVIDIA_GPU_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_tensorrt.def"',
        "process_name": "tensorrt.exe",
        "device_id": "cuda:0",
        "device_name": CUDA_DEVICES.get("cuda:0"),
        "test_name": "stable_diffusion_fp16",
        "api": "tensorrt",
    },
    "NVIDIA_GPU_XL_FP16": {
        "config": f'"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_tensorrt.def"',
        "process_name": "tensorrt.exe",
        "device_id": "cuda:0",
        "device_name": CUDA_DEVICES.get("cuda:0"),
        "test_name": "stable_diffusion_fp16_xl",
        "api": "tensorrt",
    },
}

RESULTS_FILENAME = "result.xml"
RESULTS_XML_PATH = LOG_DIR / RESULTS_FILENAME


def setup_logging():
    """setup logging"""
    setup_log_directory(str(LOG_DIR))
    logging.basicConfig(
        filename=LOG_DIR / "harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine",
        dest="engine",
        help="Engine test type",
        required=True,
        choices=BENCHMARK_CONFIG.keys(),
    )
    argies = parser.parse_args()
    return argies


def create_procyon_command(test_option, process_name, device_id):
    """create command string"""
    command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}"'

    match process_name:
        case "ort-directml.exe":
            command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-winml-device {device_id}'
        case "openvino.exe":
            command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-openvino-device {device_id}'
        case "tensorrt.exe":
            command = f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{RESULTS_XML_PATH}" --select-cuda-device {device_id}'
    command = command.rstrip()

    return command


def run_benchmark(process_name, command_to_run):
    """run the benchmark"""
    with subprocess.Popen(
        command_to_run,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as proc:
        logging.info("Procyon AI Image Generation benchmark has started.")
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
        _, _ = proc.communicate()  # blocks until 3dmark exits
        return proc


try:
    setup_logging()
    logging.info("Detected Windows ML Devices: %s", str(WINML_DEVICES))
    logging.info("Detected OpenVino Devices: %s", str(OPENVINO_DEVICES))
    logging.info("Detected CUDA Devices: %s", (CUDA_DEVICES))

    args = get_arguments()
    option = BENCHMARK_CONFIG[args.engine]["config"]
    cmd = create_procyon_command(
        option,
        BENCHMARK_CONFIG[args.engine]["process_name"],
        BENCHMARK_CONFIG[args.engine]["device_id"],
    )
    logging.info("Starting benchmark!")
    logging.info(cmd)
    start_time = time.time()
    pr = run_benchmark(BENCHMARK_CONFIG[args.engine]["process_name"], cmd)

    if pr.returncode > 0:
        logging.error("Procyon exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    score = find_score_in_xml()

    if score is None:
        logging.error("Could not find overall score!")
        sys.exit(1)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)
    am = ArtifactManager(LOG_DIR)
    am.copy_file(RESULTS_XML_PATH, ArtifactType.RESULTS_TEXT, "results xml file")
    am.create_manifest()
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)
    logging.info("Score was %s", score)

    report = {
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "test": "Procyon AI Image Generation",
        "test_parameter": BENCHMARK_CONFIG[args.engine]["test_name"],
        "api": BENCHMARK_CONFIG[args.engine]["api"],
        "test_version": find_test_version(),
        "device_name": BENCHMARK_CONFIG[args.engine]["device_name"],
        "procyon_version": find_procyon_version(),
        "unit": "score",
        "score": score,
    }

    write_report_json(str(LOG_DIR), "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
