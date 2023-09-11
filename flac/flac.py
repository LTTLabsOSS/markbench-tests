import json
import logging
import os.path
import sys
import re
import glob
import time
from subprocess import Popen

EXECUTABLE = "encode-flac.bat"
ABS_EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), EXECUTABLE)

if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    raise ValueError('No FLAC installation detected! Default installation expected to be present on the system.')


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
command = f'{ABS_EXECUTABLE_PATH}'

command = command.rstrip()
t1 = time.time()
args = []
logging.info(command)
logging.info(args)
process = Popen(executable=command, args=args, cwd=os.path.dirname(os.path.realpath(__file__)))
exit_code = process.wait()

t2 = time.time()
logging.info(f"Benchmark took {round((t2 - t1), 3)} seconds")
if exit_code > 0:
    logging.error("Test failed!")
    exit(exit_code)

result = {
    "score": round((t2 - t1), 3)
}

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()