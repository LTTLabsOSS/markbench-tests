"""Test script for c-ray"""
import json
import logging
import os.path
import subprocess
import sys
import re

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from cray_utils import current_time_ms, cray_executable_exists, copy_from_network_drive, CRAY_EXECUTABLE

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)
LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=LOGGING_FORMAT,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

if cray_executable_exists() is False:
    logging.info("Copying c-ray from network drive")
    copy_from_network_drive()

ABS_EXECUTABLE_PATH = os.path.join(script_dir, CRAY_EXECUTABLE)

# omit the first arg which is the script name
command = f'{ABS_EXECUTABLE_PATH}'
command = command.rstrip()
scores = []
start_time = current_time_ms()
for i in range(3):
    output = subprocess.check_output([command, "-s", "5120x2880", "-i", "sphfract.scn", "-o", "output.ppm"], text=True, stderr=subprocess.STDOUT)
    SCORE_PATTERN = r'Rendering.* \((\d+) milliseconds\)'
    if "seconds" in output:
        duration = re.match(SCORE_PATTERN, output).group(1)
        scores.append(float(duration))
end_time = current_time_ms()

SCORE_SUM = 0
for score in scores:
    SCORE_SUM += score
avg_score = round(SCORE_SUM / len(scores), 2)

report = {
    "start_time": start_time,
    "version": "2.0",
    "end_time": end_time,
    "score": avg_score,
    "unit": "milliseconds",
    "test": "c-ray 5120x2880"
}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as report_file:
    report_file.write(json.dumps(report))
