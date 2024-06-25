"""7-Zip test script"""
import json
import logging
import os.path
import re
import sys
import time
from subprocess import Popen
import subprocess

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from sevenzip_utils import copy_from_network_drive

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

EXECUTABLE = "7zr_24.07.exe"
ABS_EXECUTABLE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), EXECUTABLE)

if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    logging.info(
        "7-Zip executable not found, downloading from network drive")
    copy_from_network_drive()

command = f'{ABS_EXECUTABLE_PATH}'
command = command.rstrip()
t1 = time.time()
logging.info("Starting 7-Zip benchmark! This may take a minute or so...")
with Popen([command, "b", "3"], cwd=os.path.dirname(
    os.path.realpath(__file__)), stdout=subprocess.PIPE) as process:
    list_of_strings = [x.decode('utf-8').rstrip('\n')
                   for x in iter(process.stdout.readlines())]
    EXIT_CODE = process.wait()

    SPEED_PATTERN = r'^Avr:\s*([0-9]*)\s.*\|\s*([0-9]*)\s.*$'
    VERSION_PATTERN = r'7-Zip \(r\) (.*)\('

    VERSION = ""
    SPEED_C = ""
    SPEED_D = ""

    # Strips the newline character
    for line in list_of_strings:
        if line.isspace():
            continue
        logging.info(line.strip())
        if '7-Zip' in line:
            VERSION = re.match(VERSION_PATTERN, line).group(1)
        if 'Avr:' in line:
            SPEED_C = re.match(SPEED_PATTERN, line).group(1)
            SPEED_D = re.match(SPEED_PATTERN, line).group(2)

    t2 = time.time()
    logging.info("Benchmark took %s seconds", round((t2 - t1), 3))
    result = [
        {
            "test": "7-Zip Compression",
            "score": SPEED_C,
            "unit": "KiB/s",
            "version": VERSION.strip()
        },
        {
            "test": "7-Zip Decompression",
            "score": SPEED_D,
            "unit": "KiB/s",
            "version": VERSION.strip()
        },
    ]

    with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as file:
        file.write(json.dumps(result))
