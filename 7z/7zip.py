import json
import logging
import os.path
import io
import re
import glob
import time
from subprocess import Popen
import subprocess

EXECUTABLE = "7zr.exe"
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
args = ["b"]
logging.info(command)
logging.info(args)
process = Popen([command, "b"], cwd=os.path.dirname(os.path.realpath(__file__)), stdout=subprocess.PIPE)
list_of_strings = [x.decode('utf-8').rstrip('\n') for x in iter(process.stdout.readlines())]
# exit_code = process.wait()

speed_pattern = '^Avr:\s*([0-9]*)\s.*\|\s*([0-9]*)\s.*$'

speedC = ""
speedD = ""

# Strips the newline character
for line in list_of_strings:
    print(line)
    if ('Avr:' in line):
        speedC = re.match(speed_pattern, line).group(1)
        speedD = re.match(speed_pattern, line).group(2)

t2 = time.time()
logging.info(f"Benchmark took {round((t2 - t1), 3)} seconds")
result = {
    "score": speedC + " Compression (KiB/s) | " + speedD + " Decompression (KiB/s)"
}

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()