"""Test script for y-cruncher"""

import logging
import re
import sys
from pathlib import Path
from subprocess import PIPE, Popen

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



def match_time(subject: str, marker: str) -> float:
    """Extract the seconds value that follows an exact marker string."""
    pattern = rf"{re.escape(marker)}:\s*([\d.]+)\s+seconds"
    match = re.search(pattern, subject)
    if match is None:
        raise ValueError(
            f"y-cruncher output format changed: "
            f"could not parse time from line: {subject!r}"
        )
    return float(match.group(1))


def match_tune(subject: str, marker: str) -> str:
    """Extract the tuning value preceding any '=>' resolution suffix."""
    pattern = rf"{re.escape(marker)}:\s*(.*?)\s*(?:=>.*)?$"
    match = re.search(pattern, subject)
    if match is None:
        raise ValueError(
            f"y-cruncher output format changed: "
            f"could not parse tuning from line: {subject!r}"
        )
    return match.group(1).strip()


def main():
    """Test script entrypoint"""
    setup_logging(LOG_DIRECTORY)
    session_report = []
    test_types = ["bench", "bench-bbp"]

    if not ycruncher_folder_exists():
        logger.info("Downloading ycruncher")
        download_ycruncher()

    executable_path = str(get_ycruncher_executable())
    logger.info(sys.argv[1:])

    for test_type in test_types:
        start_time = current_time_ms()
        scores = []
        tunings = []
        time_marker = (
            "Total Computation Time" if test_type == "bench" else "Total Time"
        )
        tuning_marker = "Tuning Profile"
        test_result_folder = ARTIFACTS_DIRECTORY / test_type
        test_result_folder.mkdir(parents=True, exist_ok=True)

        for i in range(5):
            test_result = test_result_folder / f"{test_type}-{i}.txt"
            command = [executable_path, "skip-warnings", f'logfile:"{test_result}"', test_type, "1b"]
            logger.info(command)
            with Popen(command, stdout=PIPE, stderr=PIPE) as process:
                out, err = process.communicate()
                exit_code = process.wait()
                
                if exit_code != 0:
                    logger.error("Test failed with exit code %s", exit_code)
                    logger.info("stdout:\n%s", out.decode(errors="replace"))
                    logger.error("stderr:\n%s", err.decode(errors="replace"))
                    sys.exit(exit_code)

            with test_result.open(encoding="utf-8") as file:
                for line in file.readlines():
                    if time_marker in line:
                        scores.append(match_time(line, time_marker))
                    if tuning_marker in line:
                        tunings.append(match_tune(line, tuning_marker))
        end_time = current_time_ms()

        if not scores:
            raise RuntimeError("No scores parsed from y-cruncher output")
        if not tunings:
            raise RuntimeError("No tuning info parsed from y-cruncher output")

        avg_score = round(sum(scores) / len(scores), 2)

        logger.info("Result for %s was average %s seconds over 5 runs.", friendly_test_name(test_type), avg_score)

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
