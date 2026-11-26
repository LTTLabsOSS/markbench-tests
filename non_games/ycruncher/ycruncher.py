"""Test script for y-cruncher"""

import logging
import re
import sys
from pathlib import Path
from subprocess import Popen

from ycruncher_utils import (
    YCRUNCHER_VERSION,
    current_time_ms,
    download_ycruncher,
    get_ycruncher_executable,
    ycruncher_folder_exists,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.report import write_report_json

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)



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
    setup_logging(LOG_DIRECTORY)

    if not ycruncher_folder_exists():
        logger.info("Downloading ycruncher")
        download_ycruncher()

    executable_path = str(get_ycruncher_executable())
    # omit the first arg which is the script name
    logger.info(sys.argv[1:])

    command = [executable_path, "skip-warnings", "bench", "1b", "-o", str(LOG_DIRECTORY)]

    logger.info(command)
    scores = []
    tunings = []
    start_time = current_time_ms()
    for _ in range(5):
        with Popen(command) as process:
            exit_code = process.wait()
            if exit_code != 0:
                logger.error("Test failed with exit code %s", exit_code)
                sys.exit(exit_code)

        latest_file = max(
            LOG_DIRECTORY.glob("*.txt"), key=lambda item: item.stat().st_ctime
        )
        logger.info(latest_file)

        with latest_file.open(encoding="utf-8") as file:
            for line in file.readlines():
                if "Total Computation Time" in line:
                    scores.append(float(match_time(line)))
                if "Binary:" in line:
                    tunings.append(match_tune(line))
    end_time = current_time_ms()

    if not scores:
        raise RuntimeError("No scores parsed from y-cruncher output")

    avg_score = round(sum(scores) / len(scores), 2)

    report = {
        "start_time": start_time,
        "version": YCRUNCHER_VERSION,
        "end_time": end_time,
        "score": avg_score,
        "unit": "seconds",
        "test": "y-cruncher",
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    main()
