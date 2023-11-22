"""MSI Kombustor test script"""
from subprocess import Popen
import os
import logging
import sys
from pathlib import Path
from msi_kombustor_utils import (
    parse_args,
    parse_resolution,
    parse_score,
    create_arg_string
)

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.output import (
    write_report_json,
    format_resolution
)

INSTALL_DIR = r"C:\Program Files\Geeks3D\MSI Kombustor 4 x64"
EXECUTABLE = "MSI-Kombustor-x64.exe"

args = parse_args()

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


cmd = f'{INSTALL_DIR}/{EXECUTABLE}'

h, w = parse_resolution(args.resolution)
argstr = create_arg_string(w, h, args.test, args.benchmark)

with Popen([cmd, argstr]) as process:
    EXIT_CODE = process.wait()

log_path = os.path.join(INSTALL_DIR, "_kombustor_log.txt")
score = parse_score(log_path)

report = {
    "resolution": format_resolution(w, h),
    "test": args.test,
    "score": score
}

write_report_json(log_dir, "report.json", report)
