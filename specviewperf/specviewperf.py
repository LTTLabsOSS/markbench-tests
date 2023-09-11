import json
import logging
import os.path
import io
import re
import glob
import time
from subprocess import Popen
import subprocess

EXECUTABLE = "launch.bat"
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

if exit_code > 0:
    logging.error("Test failed!")
    exit(exit_code)

list_of_files = glob.glob("C:\\SPEC\\SPECgpc\\SPECviewperf2020\\results_*")
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)

f = open(os.path.join("C:\\SPEC\\SPECgpc\\SPECviewperf2020", latest_file, "resultCSV.csv"), "r")
Lines = f.readlines()

data_pattern = '^(.*),(.*)$'
result = {
}

first = True
# Strips the newline character
for line in Lines:
    if (first == False and len(line) > 1):
        d = re.match(data_pattern, line)
        result[d.group(1)] = d.group(2)
    elif first == True:
        first = False
    else:
        break

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()