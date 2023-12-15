"""3DMark test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import subprocess
import sys
import time
import psutil
from utils import get_score, is_process_running

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
DIR_3DMARK = Path(r"C:\\Program Files\\UL\3DMark\\")
EXECUTABLE = "3DMarkCmd.exe"
ABS_EXECUTABLE_PATH = DIR_3DMARK / EXECUTABLE
CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "TimeSpy": {
        "config": CONFIG_DIR / "timespy.3dmdef",
        "process_name":  "3DMarkTimeSpy.exe",
        "score_name": "TimeSpyPerformanceGraphicsScore"
    },
    "FireStrike": {
        "config": CONFIG_DIR / "firestrike.3dmdef",
        "process_name":  "3DMarkICFWorkload.exe",
        "score_name": "firestrikegraphicsscorep"
    },
    "PortRoyal": {
        "config": CONFIG_DIR / "portroyal.3dmdef",
        "process_name":  "3DMarkPortRoyal.exe",
        "score_name": "PortRoyalPerformanceGraphicsScore"
    },
    "SolarBay": {
        "config": CONFIG_DIR / "solarbay.3dmdef",
        "process_name":  "3DMarkSolarBay.exe",
        "score_name": "SolarBayPerformanceGraphicsScore"
    }
}
RESULTS_FILENAME = "myresults.xml"
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
        "--benchmark", dest="benchmark", help="Benchmark test type", required=True, choices=BENCHMARK_CONFIG.keys())
    argies = parser.parse_args()
    return argies


def create_3dmark_command(test_option):
    """create command string"""
    command = f'\"{ABS_EXECUTABLE_PATH}\" --definition={test_option} --export=\"{REPORT_PATH}\"'
    command = command.rstrip()
    return command


def run_benchmark(process_name, command_to_run):
    """run the benchmark"""
    with subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as proc:
        logging.info("3DMark has started.")
        start_time = time.time()
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 30: #seconds
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
    option = BENCHMARK_CONFIG[args.benchmark]["config"]
    cmd = create_3dmark_command(option)
    logging.info('Starting benchmark!')
    logging.info(cmd)
    strt = time.time()
    pr = run_benchmark(BENCHMARK_CONFIG[args.benchmark]["process_name"], cmd)

    if pr.returncode > 0:
        logging.error("3DMark exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    score = get_score(BENCHMARK_CONFIG[args.benchmark]["score_name"], REPORT_PATH)
    if score is None:
        logging.error("Could not find average FPS output!")
        sys.exit(1)

    end_time = time.time()
    elapsed_test_time = round(end_time - strt, 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)
    logging.info("Score was %s", score)

    report = {
        "test": args.benchmark,
        "score": score,
        "start_time": seconds_to_milliseconds(strt),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIR, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
