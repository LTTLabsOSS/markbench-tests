
from multiprocessing.sharedctypes import Value
import subprocess
import os
import logging
import re
import json
from argparse import ArgumentParser

"""
Parsin` arguments!
"""
parser = ArgumentParser()
parser.add_argument("-p", "--test", dest="test", help="test", metavar="test", required=True)
parser.add_argument("-r", "--minduration", dest="minduration", help="minduration", metavar="minduration", required=False)
args = parser.parse_args()

"""
Setting up some directories and logging what-have-yous
"""
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

"""
Running cinebench
"""
# See https://www.maxon.net/en/cinebench-tech-info for CLI options
# g_CinebenchCpu1Test=true – runs only the Single Core test procedure
# g_CinebenchCpuXTest=true – runs only the Multi Core test procedure
# g_CinebenchAllTests=true – runs all test procedures sequentially
# g_CinebenchMinimumTestDuration=100 – sets a minimum test duration of 100 seconds

test_options = {
    "singlecore": "g_CinebenchCpu1Test=true",
    "multicore": "g_CinebenchCpuXTest=true",
    "alltests": "g_CinebenchAllTests=true"
}

if args.test not in test_options:
    logging.error(f"Unrecognized test: {args.test}")
    exit(1)

opts = [test_options[args.test]]

# isdigit() ensures the value has no decimal as well
if args.minduration != None and not args.minduration.isdigit():
    logging.error(f"Minimum duration must be a whole number: {args.minduration}")
    exit(1)
elif args.minduration != None:
    opts = [*opts, f"g_CinebenchMinimumTestDuration={args.minduration}"]

logging.info(opts)
result = subprocess.run(["C:\\CinebenchR23\\Cinebench.exe", *opts], capture_output=True)
if result.returncode > 0:
    logging.error("Cinebench failed to run!")
    exit(result.returncode)

"""
Parsing the output of the run
"""

f = open(os.path.join(log_dir, "cinebenchlog.txt"), "wb")
f.write(result.stdout)
f.close

scorepattern = re.compile(r"^CB (\d+\.\d+) \(.+\)$")
testtitlepattern = re.compile(r"Running (\w+) CPU Render Test\.\.\.")
output = result.stdout.decode()
scorestack = []
for line in reversed(output.splitlines()):
    match = scorepattern.search(line)
    if match:
        scorestack.append(match.group(1))
        continue
    match2 = testtitlepattern.search(line)
    if match2:
        scorestack.append(match2.group(1))
        continue

if len(scorestack) % 2 > 0:
    logging.warn("Could not extract scores! Too many results found")

scores = []
i = 0
while i < len(scorestack) - 1:
    scores.append(f"{scorestack[i + 1]}:{scorestack[i]}")
    i += 2

result = {
    "test": args.test,
    "score": scores
}

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(result))
f.close()