"""Cinebench 2026 test script"""

import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from cinebench_2026_stress_utils import friendly_test_name

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes

CINEBENCH_PATH = r"C:\Cinebench2026\Cinebench.exe"
GPU_TEST = "g_CinebenchGpuTest=true"
CPU_1_TEST = "g_CinebenchCpu1Test=true"
CPU_X_TEST = "g_CinebenchCpuXTest=true"
CPU_1SMT_TEST = "g_CinebenchCpuSMTTest=true"
TEST_OPTIONS = {
    "cpu-single-thread": CPU_1_TEST,
    "cpu-single-core": CPU_1SMT_TEST,
    "cpu-multi-thread": CPU_X_TEST,
    "gpu": GPU_TEST,
}
DURATION_OPTION = "g_CinebenchMinimumTestDuration=1"


parser = ArgumentParser()
parser.add_argument(
    "-t",
    "--test",
    dest="test",
    help="Cinebench test type",
    required=True,
    choices=TEST_OPTIONS.keys(),
)
parser.add_argument(
    "--duration-seconds",
    "--duration_seconds",
    dest="duration_seconds",
    help="Stress duration in seconds",
    type=int,
    default=900,
)
args = parser.parse_args()

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)


def cpu_supports_smt() -> bool:
    """Returns True if CPU supports SMT (hyperthreading)."""
    try:
        # physical cores vs logical cores
        physical = psutil.cpu_count(logical=False)
        logical = psutil.cpu_count(logical=True)
        return logical > physical
    except Exception:
        return False


test_type = TEST_OPTIONS[args.test]

# If the test includes SMT but CPU has no hyperthreading, skip it
if test_type == CPU_1SMT_TEST and not cpu_supports_smt():
    logging.error("CPU does not support SMT. Cannot run single-core SMT test.")
    sys.exit(1)

try:
    logging.info("Stress duration: %d seconds", args.duration_seconds)
    start_time = end_time = time.time()
    while time.time() - start_time < args.duration_seconds:
        remaining_seconds = args.duration_seconds - (time.time() - start_time)
        with subprocess.Popen(
            [CINEBENCH_PATH, test_type, DURATION_OPTION],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            cwd=str(Path(CINEBENCH_PATH).parent),
            universal_newlines=True,
        ) as proc:
            logging.info(
                "Cinebench started. Setting process priority to high (PID: %s)",
                proc.pid,
            )
            process = psutil.Process(proc.pid)
            process.nice(psutil.HIGH_PRIORITY_CLASS)
            try:
                out, _ = proc.communicate(timeout=remaining_seconds)
            except subprocess.TimeoutExpired:
                logging.info("Stress duration reached. Terminating Cinebench.")
                terminate_processes(Path(CINEBENCH_PATH).name)
                proc.kill()
                out, _ = proc.communicate()

            if proc.returncode > 0:
                logging.debug("Cinebench exited with return code %d", proc.returncode)

    end_time = time.time()
    logging.info("Finished Cinebench stress test: %s", friendly_test_name(test_type))
    report = {
        "test": "Cinebench 2026 Stress",
        "test_parameter": friendly_test_name(test_type),
        "stress_duration_seconds": args.duration_seconds,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
