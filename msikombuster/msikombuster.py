"""Kombustor test script"""
import json
import logging
import os
import re
from argparse import ArgumentParser
from subprocess import Popen

flags = [
    "-width=",
    "-height=",
    "-benchmark",
    "-<test name>",
    # Start the artifact scanner
    "-scan" "-tempgraph"
    # Write GPU data (GPU temperature, FPS, etc.) to the log file every second.
    "-log_gpu_data"
    # The score file is not updated at the end of a benchmark.
    "-update_score_file_disabled"
    # By default the log file is saved in the user’s
    # temp folder (C:\Users\USER_NAME\AppData\
    # Local\Temp). This option allows to save the log
    # file in Kombustor folder
    "-logfile_in_app_folder",
]

avail_tests = [
    "vkfurrytorus",
    "glfurrytorus",
    "vkfurrymsi",
    "glfurrymsi",
    "glfurmark1700mb",
    "glfurmark3200mb",
    "glfurmark5200mb",
    "glfurmark6500mb",
    "glmsi01burn",
    "glmsi01",
    "glmsi02cpumedium",
    "glmsi02cpumedium++",
    "glmsi02gpumedium",
    "glmsi02gpumedium++",
    "glmsi02cpuhard",
    "glmsi02gpuhard",
    "glphongdonut",
    "vkphongdonut",
    "glpbrdonut",
    "vktessyspherex32",
    "vktessyspherex16",
    "gltessyspherex32",
    "gltessyspherex16",
]

INSTALL_DIR = "C:\Program Files\Geeks3D\MSI Kombustor 4 x64"
EXECUTABLE = "MSI-Kombustor-x64.exe"

parser = ArgumentParser()
parser.add_argument(
    "-t", "--test", dest="test", help="kombuster test", metavar="test", required=True
)
parser.add_argument(
    "-r",
    "--resolution",
    dest="resolution",
    help="resolution",
    metavar="resolution",
    required=True,
)
parser.add_argument(
    "-b",
    "--benchmark",
    dest="benchmark",
    help="benchmark mode",
    metavar="benchmark",
    required=False,
)
args = parser.parse_args()

if args.test not in avail_tests:
    raise ValueError(f"Error, unknown test: {args.test}")

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

match = re.search(r"^\d+,\d+$", args.resolution)
if match is None:
    raise ValueError("Resolution value must be in format height,width")
r = args.resolution.split(",")
h = r[0]
w = r[1]

cmd = f"{INSTALL_DIR}/{EXECUTABLE}"
argstr = f"-width={w} -height={h} -{args.test} -logfile_in_app_folder "
if args.benchmark == "true":
    argstr += "-benchmark"

print(cmd)
print(argstr)
process = Popen([cmd, argstr])
EXIT_CODE = process.wait()

SCORE = "N/A"
# need to find "score => 1212 points"
pattern = re.compile(r"score => (\d+)")
log_path = os.path.join(INSTALL_DIR, "_kombustor_log.txt")
with open(log_path, encoding="utf-8") as log:
    lines = log.readlines()
    for line in reversed(lines):
        match = pattern.search(line)
        if match:
            score = match.group(1)

report = {
    "resolution": f"{w}x{h}",
    "graphics_preset": "N/A",
    "test": args.test,
    "score": score,
}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps(report))
