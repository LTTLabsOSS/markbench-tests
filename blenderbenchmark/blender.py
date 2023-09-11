from argparse import ArgumentParser
import json
import logging
import os.path
import subprocess
import sys
import re
import glob
from subprocess import Popen


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
EXECUTABLE = "benchmark-launcher-cli.exe"
ABS_EXECUTABLE_PATH = os.path.join(SCRIPT_DIR, EXECUTABLE)

if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    raise ValueError('No Blender Benchmark CLI installation detected! Default installation expected to be present on the system.')

log_dir = os.path.join(SCRIPT_DIR, "run")
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
parser = ArgumentParser()
parser.add_argument("-s", "--scene", dest="scene",
                    help="blender scene", metavar="scene", required=True)
parser.add_argument("-d", "--device", dest="device",
                    help="device", metavar="device", required=True)
parser.add_argument("-v", "--version", dest="version",
                    help="version", metavar="version", required=True)

args = parser.parse_args()

version = ""
scene = []
device_type = ""

logging.info(f"Downloading Blender {args.version}")
run_array = [ABS_EXECUTABLE_PATH, "blender", "download", args.version]
process = subprocess.run(run_array, capture_output=True, text=True)

if process.returncode > 0:
    logging.info(process.stdout)
    logging.info(process.stderr)
    logging.error("Test failed!")

if args.scene.lower() == "all":
    scene = ["monster", "classroom", "junkshop"]
else:
    scene = [args.scene]

if args.device.lower() == "cpu":
    device_type = "CPU"
else:
    run_array = [ABS_EXECUTABLE_PATH, "devices", "-b", args.version]
    process = subprocess.run(run_array, capture_output=True, text=True)

    if process.returncode > 0:
        logging.info(process.stdout)
        logging.info(process.stderr)
        logging.error("Test failed!")
    else:
        logging.info(process.stdout)
        logging.info(process.stderr)
        if "OPTIX" in process.stdout or "OPTIX" in process.stderr:
            device_type = "OPTIX" # nvidia
        else:
            device_type = "HIP" # amd

logging.info(scene)
logging.info([ABS_EXECUTABLE_PATH, "benchmark"] + scene)
# download version
# .\benchmark-launcher-cli.exe blender download 3.5.0

arg_string = ["blender", "list"]
# "monster", "junkshop"
run_array = [ABS_EXECUTABLE_PATH, "benchmark"] + scene + ["-b", args.version, "--device-type", device_type, "--json"]
logging.info(f"Running with arguments {run_array}")
process = subprocess.run(run_array, capture_output=True, text=True)

if process.returncode > 0:
    logging.error(process.stderr)
    logging.error("Test failed!")
   
json_array= json.loads(process.stdout)

results = []
for report in json_array:
    result = {
        "timestamp": report['timestamp'],
        "version": report['blender_version']['version'],
        "scene": report['scene']['label'],
        "score": round(report['stats']['samples_per_minute'], 2),
        "device": report['device_info']['compute_devices'][0]['name']
    }

    logging.info(json.dumps(result, indent=2))
    result['version_json'] = report['blender_version']
    result['results_json'] = report['stats']
    results.append(result)

f = open(os.path.join(log_dir, "report.json"), "w")
f.write(json.dumps(results))
f.close()

logging.info('Test finished!')