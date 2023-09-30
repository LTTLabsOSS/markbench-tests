"""Superposition test script"""
import json
import logging
import os
import re
import sys
from argparse import ArgumentParser
from subprocess import Popen

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
parser.add_argument(
    "-r",
    "--resolution",
    dest="resolution",
    help="resolution",
    metavar="resolution",
    required=True,
)
args = parser.parse_args()

if args.preset not in avail_presets:
    raise ValueError(f"Error, unknown preset: {args.preset}")

match = re.search(r"^\d+,\d+$", args.resolution)
if match is None:
    raise ValueError("Resolution value must be in format height,width")
r = args.resolution.split(",")
h = r[0]
w = r[1]

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

cmd = f"{INSTALL_DIR}\\{EXECUTABLE}"
argstr = f"-fullscreen 1 -mode default -api {args.api} -quality {args.preset} -resolution {w}x{h}"
argstr += f" -log_txt {log_dir}\\log.txt"

logging.info(cmd)
logging.info(argstr)
argies = argstr.split(" ")
cmd = cmd.rstrip()
process = Popen([cmd, *argies])
EXIT_CODE = process.wait()

if EXIT_CODE > 0:
    logging.error("Test failed!")
    sys.exit(EXIT_CODE)

pattern = re.compile(r"Score: (\d+)")
log_path = os.path.join(log_dir, "log.txt")
with open(log_path, encoding="utf-8") as log:
    lines = log.readlines()
    for line in lines:
        match = pattern.search(line)
        if match:
            score = match.group(1)

report = {"resolution": f"{w}x{h}", "graphics_preset": args.preset, "score": score}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as file:
    file.write(json.dumps(report))
