"""Test script for primesieve"""
import json
import logging
import os.path
import subprocess
import sys
import time
import psutil

sys.path.insert(1, os.path.join(sys.path[0], ".."))

def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)

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

# if primesieve_folder_exists() is False:
#     logging.info("Downloading primesieve")
#     download_primesieve()

ABS_EXECUTABLE_PATH = os.path.join(script_dir, "xz.exe")

scores = []
start_time = current_time_ms()
command = [ABS_EXECUTABLE_PATH, "-7", "-z", "-k", "-f", "-T1", "DNDS1FINAL.mov"]
processors = [0, 1, 2, 3, 4, 5]
COUNT = 0

for i in range(5):
    with subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True) as xz_proc:
        t1 = current_time_ms()
        process = psutil.Process(xz_proc.pid)
        process.cpu_affinity([processors[COUNT]])
        out, _ = xz_proc.communicate()
        t2 = current_time_ms()
        scores.append(t2 - t1)
        COUNT += 1
end_time = current_time_ms()

SCORE_SUM = 0
for score in scores:
    print(score)
    SCORE_SUM += score
avg_score = round(SCORE_SUM / len(scores), 2)

report = {
    "start_time": start_time,
    "version": "12.3",
    "end_time": end_time,
    "score": avg_score,
    "unit": "milliseconds",
    "test": "XZ Compression"
}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as report_file:
    report_file.write(json.dumps(report))
