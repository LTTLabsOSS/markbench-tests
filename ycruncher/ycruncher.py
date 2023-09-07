import json
import logging
import os.path
import sys
import re
import glob
from subprocess import Popen

EXEC_DIR = "y-cruncherv0.7.10.9513"
EXECUTABLE = "y-cruncher.exe"
ABS_EXECUTABLE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), EXEC_DIR, EXECUTABLE)

if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    raise ValueError('No y-cruncher installation detected! Default installation expected to be present on the system.')

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
logging.info(args)
command = f'{ABS_EXECUTABLE_PATH}'

command = command.rstrip()

arg_string = ['skip-warnings', 'bench', '5b', '-o', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run')]

logging.info(arg_string)
process = Popen(executable=command, args=arg_string)
exit_code = process.wait()

if exit_code > 0:
    logging.error("Test failed!")
    exit(exit_code)

list_of_files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run','*.txt'))
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)

f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run', latest_file), "r")
Lines = f.readlines()

time_pattern = '^.*:\s*(.*) seconds$'
tune_pattern = '^.*:\s*(.*)$'
time = ""
tuning = ""

# Strips the newline character
for line in Lines:
    if ('Total Computation Time' in line):
        time = re.match(time_pattern, line).group(1)
    if ('Tuning:' in line):
        tuning = re.match(tune_pattern, line).group(1)

f.close()

result = {
    "score": time,
    "test": tuning
}

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()