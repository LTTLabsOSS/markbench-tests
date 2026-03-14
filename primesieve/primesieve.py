"""Test script for primesieve"""

import json
import logging
from pathlib import Path
import subprocess
import sys
import re

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from primesieve_utils import (
    PRIMESIEVE_FOLDER_NAME,
    current_time_ms,
    download_primesieve,
    primesieve_folder_exists,
)
from harness_utils.output import setup_logging

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)

if primesieve_folder_exists() is False:
    logging.info("Downloading primesieve")
    download_primesieve()

ABS_EXECUTABLE_PATH = SCRIPT_DIRECTORY / PRIMESIEVE_FOLDER_NAME / "primesieve.exe"

# omit the first arg which is the script name
command = str(ABS_EXECUTABLE_PATH)
command = command.rstrip()
scores = []
start_time = current_time_ms()
for i in range(3):
    output = subprocess.check_output([command, "1e12", "--quiet", "--time"], text=True)
    SCORE_PATTERN = r"Seconds:\s(\d+\.\d+)"
    if "Seconds" in output:
        duration = re.match(SCORE_PATTERN, output).group(1)
        scores.append(float(duration))
end_time = current_time_ms()

SCORE_SUM = 0
for score in scores:
    SCORE_SUM += score
avg_score = round(SCORE_SUM / len(scores), 2)

report = {
    "start_time": start_time,
    "version": "12.3",
    "end_time": end_time,
    "score": avg_score,
    "unit": "seconds",
    "test": "Primesieve 1e12",
}

with open(LOG_DIRECTORY / "report.json", "w", encoding="utf-8") as report_file:
    report_file.write(json.dumps(report))
