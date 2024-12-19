"""3DMark test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import subprocess
import sys
import time
import psutil
from utils import find_score_in_xml, is_process_running, get_install_path, get_winml_devices

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

WINML_DEVICES = get_winml_devices(ABS_EXECUTABLE_PATH)

CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "AMD_CPU": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_winml_cpu.def\"",
        "process_name":  "WinML.exe",
        "test_name": "WinML CPU (FLOAT32)"
    },
    "AMD_GPU0": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_winml_gpu.def\"",
        "process_name":  "WinML.exe",
        "device_name": list(WINML_DEVICES.keys())[0],
        "device_id": list(WINML_DEVICES.values())[0],
        "test_name": "WinML GPU (FLOAT32)"
    },
    "AMD_GPU1": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_winml_gpu.def\"",
        "process_name":  "WinML.exe",
        "device_name": list(WINML_DEVICES.keys())[1],
        "device_id": list(WINML_DEVICES.values())[1],
        "test_name": "WinML GPU (FLOAT32)"
    },
    "Intel_CPU": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_openvino_cpu.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO CPU (FLOAT32)"
    },
    "Intel_GPU0": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_openvino_gpu.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO GPU 0 (FLOAT32)"
    },
    "Intel_GPU1": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_openvino_gpu.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO GPU 1 (FLOAT32)"
    },
    "Intel_NPU": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_openvino_npu.def\"",
        "process_name":  "OpenVino.exe",
        "test_name": "Intel OpenVINO NPU (FLOAT32)"
    },
    "NVIDIA_GPU": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_tensorrt.def\"",
        "process_name":  "TensorRT.exe",
        "test_name": "NVIDIA TensorRT (FLOAT32)"
    },
    "Qualcomm_HTP": {
        "config": f"\"{CONFIG_DIR}\\ai_computer_vision_snpe.def\"",
        "process_name":  "SNPE.exe",
        "test_name": "Qualcomm SNPE (INTEGER)"
    },
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


def create_procyon_command(test_option, process_name, device_id):
    """create command string"""
    match process_name:
        case 'WinML.exe':
            command = f'\"{ABS_EXECUTABLE_PATH}\" --definition={test_option} --export=\"{REPORT_PATH}\" --select-winml-device {device_id}'
        case 'OpenVino.exe':
            command = f'\"{ABS_EXECUTABLE_PATH}\" --definition={test_option} --export=\"{REPORT_PATH}\" --select-openvino-device {device_id}'
        case 'TensorRT.exe':
            command = f'\"{ABS_EXECUTABLE_PATH}\" --definition={test_option} --export=\"{REPORT_PATH}\" --select-cuda-device {device_id}'
    command = command.rstrip()
    return command


def run_benchmark(process_name, command_to_run):
    """run the benchmark"""
    with subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as proc:
        logging.info("Procyon AI Computer Vision benchmark has started.")
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
    process_name = BENCHMARK_CONFIG[args.engine]["process_name"]
    device_id = BENCHMARK_CONFIG[args.engine]["device_id"]
    cmd = create_procyon_command(option, process_name, device_id)
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
        "device_name": BENCHMARK_CONFIG[args.engine]["device_name"],
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
