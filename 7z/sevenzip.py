"""7-Zip test script"""

import json
import logging
from pathlib import Path
import re
import sys
import time
from subprocess import Popen
import subprocess

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from sevenzip_utils import copy_from_network_drive
from harness_utils.output import setup_logging

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)

EXECUTABLE = "7za_64_26.00.exe"
ABS_EXECUTABLE_PATH = SCRIPT_DIRECTORY / EXECUTABLE

if ABS_EXECUTABLE_PATH.is_file() is False:
    logging.info("7-Zip executable not found, downloading from network drive")
    copy_from_network_drive()

command = str(ABS_EXECUTABLE_PATH)
command = command.rstrip()
t1 = time.time()
logging.info("Starting 7-Zip benchmark! This may take a minute or so...")
with Popen(
    [command, "b", "3"], cwd=SCRIPT_DIRECTORY, stdout=subprocess.PIPE
) as process:
    stdout_data, stderr = process.communicate()
    list_of_strings = stdout_data.decode("utf-8").splitlines()

    SPEED_PATTERN = r"^Avr:\s*([0-9]*)\s.*\|\s*([0-9]*)\s.*$"
    VERSION_PATTERN = r"7-Zip \(a\) (\d+\.\d+) \((x\d+)\).*"

    version = ""
    speed_c = ""
    speed_d = ""

    # Strips the newline character
    for line in list_of_strings:
        if line.isspace():
            continue
        logging.info(line.strip())
        if "7-Zip" in line:
            match = re.match(VERSION_PATTERN, line)
            if match:
                version = f"{match.group(1)} {match.group(2)}"
        if "Avr:" in line:
            speed_c = re.match(SPEED_PATTERN, line).group(1)
            speed_d = re.match(SPEED_PATTERN, line).group(2)

    t2 = time.time()
    logging.info("Benchmark took %s seconds", round((t2 - t1), 3))
    result = [
        {
            "test": "7-Zip Compression",
            "score": speed_c,
            "unit": "KiB/s",
            "version": version.strip(),
        },
        {
            "test": "7-Zip Decompression",
            "score": speed_d,
            "unit": "KiB/s",
            "version": version.strip(),
        },
    ]

    with open(LOG_DIRECTORY / "report.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(result))
