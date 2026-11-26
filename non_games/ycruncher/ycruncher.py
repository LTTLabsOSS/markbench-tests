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
    friendly_test_name,
    get_ycruncher_executable,
    ycruncher_folder_exists,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import create_artifacts_manifest
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
    session_report = []
    test_types = ["bench", "bench-bbp"]

    if not ycruncher_folder_exists():
        logger.info("Downloading ycruncher")
        download_ycruncher()

    executable_path = str(get_ycruncher_executable())
    # omit the first arg which is the script name
    logger.info(sys.argv[1:])

    for test_type in test_types:
        start_time = current_time_ms()
        scores = []
        tunings = []
        test_result = ARTIFACTS_DIRECTORY / test_type
        test_result.mkdir(parents=True, exist_ok=True)
        command = [executable_path, "skip-warnings", test_type, "1b", "-o", str(test_result)]
        logger.info(command)
        for _ in range(5):
            with Popen(command, stdout=PIPE, stderr=PIPE) as process:
                exit_code = process.wait()
                out, err = process.communicate()
                logger.info("exit=%s", exit_code)
                logger.info("stdout:\n%s", out.decode(errors="replace"))
                logger.error("stderr:\n%s", err.decode(errors="replace"))
                if exit_code != 0:
                    logger.error("Test failed with exit code %s", exit_code)
                    sys.exit(exit_code)

            latest_file = max(
                test_result.glob("*.txt"), key=lambda item: item.stat().st_ctime
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
        if not tunings:
            raise RuntimeError("No tuning info parsed from y-cruncher output")

        avg_score = round(sum(scores) / len(scores), 2)

        report = {
            "start_time": start_time,
            "version": YCRUNCHER_VERSION,
            "end_time": end_time,
            "score": avg_score,
            "unit": "seconds",
            "test": "Y-Cruncher",
            "test_parameter": friendly_test_name(test_type),
            "binary": tunings[0]
        }
        session_report.append(report)

    create_artifacts_manifest(
    ARTIFACTS_DIRECTORY
)

    write_report_json(LOG_DIRECTORY, "report.json", session_report)


if __name__ == "__main__":
    main()
