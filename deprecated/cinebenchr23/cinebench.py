"""CinebenchR23 test script"""
import json
import logging
import os
import re
import subprocess
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "-p", "--test", dest="test", help="test", metavar="test", required=True
)
parser.add_argument(
    "-r",
    "--minduration",
    dest="minduration",
    help="minduration",
    metavar="minduration",
    required=False,
)
args = parser.parse_args()


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

# See https://www.maxon.net/en/cinebench-tech-info for CLI options
# g_CinebenchCpu1Test=true – runs only the Single Core test procedure
# g_CinebenchCpuXTest=true – runs only the Multi Core test procedure
# g_CinebenchAllTests=true – runs all test procedures sequentially
# g_CinebenchMinimumTestDuration=100 – sets a minimum test duration of 100 seconds

test_options = {
    "singlecore": "g_CinebenchCpu1Test=true",
    "multicore": "g_CinebenchCpuXTest=true",
    "alltests": "g_CinebenchAllTests=true",
}

if args.test not in test_options:
    logging.error("Unrecognized test %s", args.test)
    sys.exit(1)

opts = [test_options[args.test]]

# isdigit() ensures the value has no decimal as well
if args.minduration is not None and not args.minduration.isdigit():
    logging.error("Minimum duration must be a whole number %s", args.minduration)
    sys.exit(1)
elif args.minduration is not None:
    opts = [*opts, f"g_CinebenchMinimumTestDuration={args.minduration}"]

logging.info(opts)
result = subprocess.run(
    ["C:\\CinebenchR23\\Cinebench.exe", *opts], capture_output=True, check=False
)
if result.returncode > 0:
    logging.error("Cinebench failed to run!")
    exit(result.returncode)


with open(os.path.join(log_dir, "cinebenchlog.txt"), "wb") as f:
    f.write(result.stdout)


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
    logging.warning("Could not extract scores! Too many results found")

scores = []
i = 0
while i < len(scorestack) - 1:
    scores.append(f"{scorestack[i + 1]}:{scorestack[i]}")
    i += 2

report = {"test": args.test, "score": scores}

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as file:
    f.write(json.dumps(report))
