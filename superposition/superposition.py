"""Superposition test script"""

import json
import logging
import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from subprocess import Popen

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import setup_logging

avail_presets = ["low", "medium", "high", "extreme", "4k_optimized", "8k_optimized"]

INSTALL_DIR = "C:\\Program Files\\Unigine\\Superposition Benchmark\\bin"
EXECUTABLE = "superposition_cli.exe"

parser = ArgumentParser()
parser.add_argument(
    "-a", "--api", dest="api", help="graphics api", metavar="api", required=True
)
parser.add_argument(
    "-p",
    "--preset",
    dest="preset",
    help="performance preset",
    metavar="preset",
    required=True,
)
args = parser.parse_args()

if args.preset not in avail_presets:
    raise ValueError(f"Error, unknown preset: {args.preset}")

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)

cmd = f"{INSTALL_DIR}\\{EXECUTABLE}"
argstr = (
    f"-fullscreen 1 -mode default -api {args.api} -quality {args.preset} -iterations 1"
)
argstr += f" -log_txt {LOG_DIRECTORY}\\log.txt"

logging.info(cmd)
logging.info(argstr)
argies = argstr.split(" ")
cmd = cmd.rstrip()
with Popen([cmd, *argies]) as process:
    EXIT_CODE = process.wait()

if EXIT_CODE > 0:
    logging.error("Test failed!")
    sys.exit(EXIT_CODE)

SCORE = ""
pattern = re.compile(r"Score: (\d+)")
LOG_PATH = LOG_DIRECTORY / "log.txt"
with open(LOG_PATH, encoding="utf-8") as log:
    lines = log.readlines()
    for line in lines:
        match = pattern.search(line)
        if match:
            SCORE = match.group(1)

report = {
    "test": "Unigine Superposition",
    "test_parameter": f"{args.api}",
    "test_preset": args.preset,
    "score": SCORE,
    "unit": "score",
}

with open(LOG_DIRECTORY / "report.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(report))
