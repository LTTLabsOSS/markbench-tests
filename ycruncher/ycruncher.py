"""Test script for y-cruncher"""
import json
import logging
import os.path
import sys
import re
import glob
from subprocess import Popen

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from ycruncher_utils import YCRUNCHER_FOLDER_NAME, download_ycruncher, ycruncher_folder_exists

ABS_EXECUTABLE_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), YCRUNCHER_FOLDER_NAME, "y-cruncher.exe")

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

if ycruncher_folder_exists() is False:
    download_ycruncher()

# omit the first arg which is the script name
args = sys.argv[1:]
logging.info(args)
command = f'{ABS_EXECUTABLE_PATH}'
command = command.rstrip()
arg_string = ['skip-warnings', 'bench', '5b', '-o',
              os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run')]

logging.info(arg_string)
with Popen(executable=command, args=arg_string) as process:
    EXIT_CODE = process.wait()

if EXIT_CODE > 0:
    logging.error("Test failed!")
    sys.exit(EXIT_CODE)

list_of_files = glob.glob(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'run', '*.txt'))
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)

with open(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'run', latest_file), "r", encoding="utf-8") as file:
    Lines = file.readlines()

TIME_PATTERN = r'^.*:\s*(.*) seconds$'
TUNE_PATTERN = r'^.*:\s*(.*)$'
TIME = ""
TUNING = ""

# Strips the newline character
for line in Lines:
    if 'Total Computation Time' in line:
        time = re.match(TIME_PATTERN, line).group(1)
    if 'Tuning:' in line:
        tuning = re.match(TUNE_PATTERN, line).group(1)

report = {
    "score": time,
    "test": tuning
}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as report_file:
    report_file.write(json.dumps(report))
