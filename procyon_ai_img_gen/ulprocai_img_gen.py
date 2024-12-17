"""3DMark test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import subprocess
import sys
import time
import psutil
from utils import find_score_in_xml, is_process_running, get_install_path

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json
)

#####
### Globals
#####
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
DIR_PROCYON = Path(get_install_path())
EXECUTABLE = "ProcyonCmd.exe"
ABS_EXECUTABLE_PATH = DIR_PROCYON / EXECUTABLE
CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "AMD_GPU_FP16": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_onnxruntime.def\"",
        "process_name":  "ort-directml.exe",
        "test_name": "ONNX Stable Diffusion FP16"
    },
    "AMD_GPU_XL_FP16": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_onnxruntime.def\"",
        "process_name": "ort-directml.exe",
        "test_name": "ONNX Stable Diffusion FP16 XL"
    },
     "Intel_GPU_INT8": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sd15int8_openvino.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO Stable Diffusion INT8"
    },
    "Intel_GPU_FP16": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_openvino.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO Stable Diffusion FP16"
    },
    "Intel_GPU_XL_FP16": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_openvino.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO Stable Diffusion FP16 XL"
    },
    "NVIDIA_GPU_INT8": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sd15int8_tensorrt.def\"",
        "process_name":  "TensorRT.exe",
        "test_name": "NVIDIA TensorRT Stable Diffusion INT8"
    },
    "NVIDIA_GPU_FP16": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sd15fp16_tensorrt.def\"",
        "process_name":  "TensorRT.exe",
        "test_name": "NVIDIA TensorRT Stable Diffusion FP16"
    },
    "NVIDIA_GPU_XL_FP16": {
        "config": f"\"{CONFIG_DIR}\\ai_imagegeneration_sdxlfp16_tensorrt.def\"",
        "process_name":  "TensorRT.exe",
        "test_name": "NVIDIA TensorRT Stable Diffusion FP16 XL"
    }
}
RESULTS_FILENAME = "result.xml"
REPORT_PATH = LOG_DIR / RESULTS_FILENAME

def setup_logging():
    """setup logging"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=LOG_DIR / "harness.log",
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine", dest="engine", help="Engine test type", required=True, choices=BENCHMARK_CONFIG.keys())
    argies = parser.parse_args()
    return argies


def create_procyon_command(test_option):
    """create command string"""
    command = f'\"{ABS_EXECUTABLE_PATH}\" --definition={test_option} --export=\"{REPORT_PATH}\"'
    command = command.rstrip()
    return command


def run_benchmark(process_name, command_to_run):
    """run the benchmark"""
    with subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as proc:
        logging.info("Procyon AI Image Generation benchmark has started.")
        start_time = time.time()
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 60: #seconds
                raise ValueError("BenchMark subprocess did not start in time")
            process = is_process_running(process_name)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)
        _, _ = proc.communicate() # blocks until 3dmark exits
        return proc

try:
    setup_logging()
    args = get_arguments()
    option = BENCHMARK_CONFIG[args.engine]["config"]
    cmd = create_procyon_command(option)
    logging.info('Starting benchmark!')
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
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)
    logging.info("Score was %s", score)

    report = {
        "test": BENCHMARK_CONFIG[args.engine]["test_name"],
        "unit": "score",
        "score": score,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIR, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
