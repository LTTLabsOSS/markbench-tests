"""Test script for primesieve"""

import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)

sys.path.insert(1, PARENT_DIRECTORY)

from primesieve_utils import (
    PRIMESIEVE_FOLDER_NAME,
    current_time_ms,
    download_primesieve,
    get_primesieve_version,
    primesieve_folder_exists,
)

from harness_utils.output_logging import setup_logging

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"

setup_logging(LOG_DIRECTORY)


if sys.platform == "win32":
    if primesieve_folder_exists() is False:
        logger.info("Downloading primesieve")
        download_primesieve()

    executable_name = "primesieve.exe"
    ABS_EXECUTABLE_PATH = (
        SCRIPT_DIRECTORY / PRIMESIEVE_FOLDER_NAME / executable_name
    )
else:
    ABS_EXECUTABLE_PATH = shutil.which("primesieve")

    if ABS_EXECUTABLE_PATH is None:
        raise RuntimeError(
            "Primesieve was not detected. "
            "Install it using your Linux package manager."
        )


command = str(ABS_EXECUTABLE_PATH)
command = command.rstrip()

version = get_primesieve_version(command)

scores = []

start_time = current_time_ms()

for i in range(3):
    output = subprocess.check_output(
        [command, "1e12", "--quiet", "--time"],
        text=True,
    )

    score_pattern = r"Seconds:\s(\d+\.\d+)"

    if "Seconds" in output:
        duration = re.match(score_pattern, output).group(1)
        scores.append(float(duration))

end_time = current_time_ms()

SCORE_SUM = 0

for score in scores:
    SCORE_SUM += score

avg_score = round(SCORE_SUM / len(scores), 2)

report = {
    "start_time": start_time,
    "version": version,
    "end_time": end_time,
    "score": avg_score,
    "unit": "seconds",
    "test": "Primesieve 1e12",
}

with open(
    LOG_DIRECTORY / "report.json",
    "w",
    encoding="utf-8",
) as report_file:
    report_file.write(json.dumps(report))