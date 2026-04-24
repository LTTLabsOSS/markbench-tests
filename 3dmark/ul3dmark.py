"""3DMark test script"""

import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from ul3dmark_utils import get_score

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import is_process_running

#####
# Globals
#####
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
DIR_3DMARK = Path(r"C:\\Program Files\\UL\3DMark\\")
EXECUTABLE = "3DMarkCmd.exe"
ABS_EXECUTABLE_PATH = DIR_3DMARK / EXECUTABLE
CONFIG_DIR = SCRIPT_DIRECTORY / "config"
BENCHMARK_CONFIG = {
    "TimeSpy": {
        "config": CONFIG_DIR / "timespy.3dmdef",
        "process_name": "3DMarkTimeSpy.exe",
        "score_name": "TimeSpyPerformanceGraphicsScore",
        "test_name": "3DMark Time Spy",
    },
    "FireStrike": {
        "config": CONFIG_DIR / "firestrike.3dmdef",
        "process_name": "3DMarkICFWorkload.exe",
        "score_name": "firestrikegraphicsscorep",
        "test_name": "3DMark Fire Strike",
    },
    "PortRoyal": {
        "config": CONFIG_DIR / "portroyal.3dmdef",
        "process_name": "3DMarkPortRoyal.exe",
        "score_name": "PortRoyalPerformanceGraphicsScore",
        "test_name": "3DMark Port Royal",
    },
    "SolarBay": {
        "config": CONFIG_DIR / "solarbay.3dmdef",
        "process_name": "3DMarkSolarBay.exe",
        "score_name": "SolarBayPerformanceGraphicsScore",
        "test_name": "3DMark Solar Bay",
    },
}
RESULTS_FILENAME = "myresults.xml"
REPORT_PATH = LOG_DIRECTORY / RESULTS_FILENAME


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--benchmark",
        dest="benchmark",
        help="Benchmark test type",
        required=True,
        choices=BENCHMARK_CONFIG.keys(),
    )
    argies = parser.parse_args()
    return argies


def create_3dmark_command(test_option):
    """create command string"""
    command = (
        f'"{ABS_EXECUTABLE_PATH}" --definition={test_option} --export="{REPORT_PATH}"'
    )
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
        logging.info("3DMark has started.")
        start_time = time.time()
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 30:  # seconds
                raise RuntimeError("Benchmark subprocess did not start in time")
            process = is_process_running(process_name)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)
        _, _ = proc.communicate()  # blocks until 3dmark exits
        return proc


def main():
    """Run the selected 3DMark benchmark."""
    setup_logging(LOG_DIRECTORY)
    args = get_arguments()
    option = BENCHMARK_CONFIG[args.benchmark]["config"]
    cmd = create_3dmark_command(option)
    logging.info("Starting benchmark!")
    logging.info(cmd)
    strt = time.time()
    pr = run_benchmark(BENCHMARK_CONFIG[args.benchmark]["process_name"], cmd)

    if pr.returncode > 0:
        logging.error("3DMark exited with return code %d", pr.returncode)
        return pr.returncode

    score = get_score(BENCHMARK_CONFIG[args.benchmark]["score_name"], REPORT_PATH)

    end_time = time.time()
    elapsed_test_time = round(end_time - strt, 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)
    logging.info("Score was %s", score)

    report = {
        "test": "3DMark",
        "test_parameter": args.benchmark,
        "unit": "score",
        "score": score,
        "start_time": seconds_to_milliseconds(strt),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
