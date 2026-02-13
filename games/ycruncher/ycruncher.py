"""Test script for y-cruncher"""

import logging
import os
import re
import sys
from pathlib import Path
from subprocess import Popen

from ycruncher_utils import (
    YCRUNCHER_FOLDER_NAME,
    current_time_ms,
    download_ycruncher,
    ycruncher_folder_exists,
)

sys.path.insert(1, os.path.join(sys.path[0], "../.."))

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    write_report_json,
)

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
EXECUTABLE_PATH = SCRIPT_DIR / YCRUNCHER_FOLDER_NAME / "y-cruncher.exe"


def setup_logging():
    """Configures root logger"""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=f"{LOG_DIR}/harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def match_time(subject: str):
    """Extract time value from line"""
    time_pattern = r"^.*:\s*(.*) seconds$"
    return re.match(time_pattern, subject).group(1)


def match_tune(subject: str):
    """Extract tuning value from line"""
    tune_pattern = r"^.*:\s*(.*)$"
    return re.match(tune_pattern, subject).group(1)


def main():
    """Test script entrypoint"""
    setup_logging()

    if not ycruncher_folder_exists():
        logging.info("Downloading ycruncher")
        download_ycruncher()

    # omit the first arg which is the script name
    logging.info(sys.argv[1:])

    arg_string = ["skip-warnings", "bench", "1b", "-o", LOG_DIR]

    logging.info(arg_string)
    scores = []
    tunings = []
    start_time = current_time_ms()
    for _ in range(5):
        with Popen(
            executable=f"{EXECUTABLE_PATH}".rstrip(), args=arg_string
        ) as process:
            exit_code = process.wait()
            if exit_code > 0:
                logging.error("Test failed!")
                sys.exit(exit_code)

        latest_file = max(LOG_DIR.glob("*.txt"), key=lambda item: item.stat().st_ctime)
        logging.info(latest_file)

        with latest_file.open(encoding="utf-8") as file:
            for line in file.readlines():
                if "Total Computation Time" in line:
                    scores.append(float(match_time(line)))
                if "Binary:" in line:
                    tunings.append(match_tune(line))
    end_time = current_time_ms()
    avg_score = round(sum(scores) / len(scores), 2)

    report = {
        "start_time": start_time,
        "version": "v0.8.5.9545b",
        "end_time": end_time,
        "score": avg_score,
        "unit": "seconds",
        "test": "y-cruncher",
    }

    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    main()
