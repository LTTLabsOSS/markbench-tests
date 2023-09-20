"""FLAC test script"""
import json
import logging
import os.path
import sys
import time
from subprocess import Popen

sys.path.insert(1, os.path.join(sys.path[0], ".."))

# pylint: disable=wrong-import-position
from flac_utils import download_flac, flac_folder_exists
from harness_utils.output import DEFAULT_LOGGING_FORMAT, setup_log_directory

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
setup_log_directory(log_dir)
logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

FLAC_URL = "https://ftp.osuosl.org/pub/xiph/releases/flac/flac-1.4.3-win.zip"
if flac_folder_exists() is False:
    download_flac(FLAC_URL)

EXECUTABLE = "encode-flac.bat"
ABS_EXECUTABLE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), EXECUTABLE)
command = f'{ABS_EXECUTABLE_PATH}'

command = command.rstrip()
start_time = time.time()
process = Popen(executable=command, args=[],
                cwd=os.path.dirname(os.path.realpath(__file__)))
EXIT_CODE = process.wait()

if EXIT_CODE > 0:
    logging.error("Test failed!")
    sys.exit(EXIT_CODE)

end_time = time.time()
score = round((end_time - start_time), 3)
logging.info("Benchmark took %s seconds", score)
if EXIT_CODE > 0:
    logging.error("Test failed!")
    exit(EXIT_CODE)

report = {
    "score": score,
    "version": "1.4.3"
}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as report_file:
    report_file.write(json.dumps(report))
