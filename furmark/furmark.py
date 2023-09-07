import json
import logging
import os.path
import sys
from subprocess import Popen

DEFAULT_FURMARK_DIR = "C:\\Program Files (x86)\\Geeks3D\\Benchmarks\\FurMark"
EXECUTABLE = "FurMark.exe"
ABS_EXECUTABLE_PATH = os.path.join(DEFAULT_FURMARK_DIR, EXECUTABLE)

if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    raise ValueError('No FurMark installation detected! Default installation expected to be present on the system.')

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

# omit the first arg which is the script name
args = sys.argv[1:]
command = f'{ABS_EXECUTABLE_PATH}'
arg_string = ""
for arg in args:
    arg_string += arg + ' '

command = command.rstrip()
logging.info(command)
process = Popen([command, arg_string])
exit_code = process.wait()

if exit_code > 0:
    logging.error("Test failed!")
    exit(exit_code)

result = {
    "resolution": "",
    "graphics_preset": ""
}

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()
