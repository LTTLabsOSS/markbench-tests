from argparse import ArgumentParser
from subprocess import Popen
import json
import re
import os
import logging

avail_presets = [
    "low",
    "medium",
    "high",
    "extreme",
    "4k_optimized",
    "8k_optimized"
]

INSTALL_DIR = "C:\\Program Files\\Unigine\\Superposition Benchmark\\bin"
EXECUTABLE = "superposition_cli.exe"

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)
logging_format = '%(asctime)s %(levelname)-s %(message)s'
logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=logging_format,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(logging_format)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

parser = ArgumentParser()
parser.add_argument("-a", "--api", dest="api",
                    help="graphics api", metavar="api", required=True)
parser.add_argument("-p", "--preset", dest="preset",
                    help="performance preset", metavar="preset", required=True)
parser.add_argument("-r", "--resolution", dest="resolution",
                    help="resolution", metavar="resolution", required=True)
args = parser.parse_args()

if args.preset not in avail_presets:
    raise ValueError(f"Error, unknown preset: {args.preset}")

match = re.search("^\d+,\d+$", args.resolution)
if match is None:
    raise ValueError("Resolution value must be in format height,width")
r = args.resolution.split(",")
h = r[0]
w = r[1]

cmd = f'{INSTALL_DIR}\\{EXECUTABLE}'
argstr = f"-fullscreen 1 -mode default -api {args.api} -quality {args.preset} -resolution {w}x{h}"
argstr += f" -log_txt {log_dir}\\log.txt"

logging.info(cmd)
logging.info(argstr)
argies = argstr.split(" ")
cmd = cmd.rstrip()
process = Popen([cmd, *argies])
exit_code = process.wait()

if exit_code > 0:
    logging.error("Test failed!")
    exit(exit_code)

pattern = re.compile(r"Score: (\d+)")
log_path = os.path.join(log_dir, "log.txt")
log = open(log_path)
lines = log.readlines()
for line in lines:
    match = pattern.search(line)
    if match:
        score = match.group(1)
log.close()

result = {
    "resolution": f"{w}x{h}",
    "graphics_preset": args.preset,
    "score": score
}

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()

