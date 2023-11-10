"""Cinebench 2024 test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import subprocess
import sys
import time
import psutil
from cinebench_utils import get_score

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    write_report_json
)

CINEBENCH_PATH = r"C:\Cinebench2024\Cinebench.exe"
TEST_OPTIONS = {
    "cpu-single-core": "g_CinebenchCpu1Test=true",
    "cpu-multi-core": "g_CinebenchCpuXTest=true",
    "gpu": "g_CinebenchGpuTest=true"
}
DURATION_OPTION = "g_CinebenchMinimumTestDuration=1"

parser = ArgumentParser()
parser.add_argument(
    "-t", "--test", dest="test", help="Cinebench test type", required=True, choices=TEST_OPTIONS.keys())
args = parser.parse_args()

script_dir = Path(__file__).resolve().parent
log_dir = script_dir / "run"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "harness.log"
logging.basicConfig(
    filename=log_file,
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

test_option = TEST_OPTIONS[args.test]

try:
    logging.info('Starting benchmark!')
    setup_start_time = time.time()

    with subprocess.Popen(
        [CINEBENCH_PATH, test_option, DURATION_OPTION],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True) as proc:
        logging.info("Cinebench started. Waiting for setup to finish to set process priority.")
        for line in proc.stdout:
            if "BEFORERENDERING" in line:
                elapsed_setup_time = round(time.time() - setup_start_time, 2)
                logging.info("Setup took %.2f seconds", elapsed_setup_time)
                logging.info("Setting Cinebench process priority to high (PID: %s)", proc.pid)
                process = psutil.Process(proc.pid)
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                start_time = time.time()
                break
        out, _ = proc.communicate()

        if proc.returncode > 0:
            logging.error("Cinebench exited with return code %d", proc.returncode)
            sys.exit(proc.returncode)

        score = get_score(out)
        if score is None:
            logging.error("Could not find score in Cinebench output!")
            sys.exit(1)

        end_time = time.time()
        elapsed_test_time = round(end_time - start_time, 2)
        logging.info("Benchmark took %.2f seconds", elapsed_test_time)

        report = {
            "test": args.test,
            "score": score,
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time)
        }

        write_report_json(log_dir, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
