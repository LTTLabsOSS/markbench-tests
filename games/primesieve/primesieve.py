"""Test script for primesieve"""

import json
import logging
import os.path
import re
import subprocess
import sys

sys.path.insert(1, os.path.join(sys.path[0], "../.."))

from primesieve_utils import (
    PRIMESIEVE_FOLDER_NAME,
    current_time_ms,
    download_primesieve,
    primesieve_folder_exists,
)

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)
LOGGING_FORMAT = "%(asctime)s %(levelname)-s %(message)s"
logging.basicConfig(
    filename=f"{log_dir}/harness.log",
    format=LOGGING_FORMAT,
    datefmt="%m-%d %H:%M",
    level=logging.DEBUG,
)
console = logging.StreamHandler()
formatter = logging.Formatter(LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

if primesieve_folder_exists() is False:
    logging.info("Downloading primesieve")
    download_primesieve()

ABS_EXECUTABLE_PATH = os.path.join(script_dir, PRIMESIEVE_FOLDER_NAME, "primesieve.exe")

# omit the first arg which is the script name
command = f"{ABS_EXECUTABLE_PATH}"
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

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as report_file:
    report_file.write(json.dumps(report))
