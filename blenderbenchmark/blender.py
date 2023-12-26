"""Blender benchmark test script"""
from argparse import ArgumentParser
import json
import logging
import os.path
import subprocess
from zipfile import ZipFile
import requests

# omit the first arg which is the script name
parser = ArgumentParser()
parser.add_argument("-s", "--scene", dest="scene",
                    help="blender scene", metavar="scene", required=True)
parser.add_argument("-d", "--device", dest="device",
                    help="device", metavar="device", required=True)
parser.add_argument("-v", "--version", dest="version",
                    help="version", metavar="version", required=True)

args = parser.parse_args()

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(SCRIPT_DIR, "run")
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

EXECUTABLE = "benchmark-launcher-cli.exe"
ABS_EXECUTABLE_PATH = os.path.join(SCRIPT_DIR, EXECUTABLE)


def download_and_extract_cli():
    """Downloads and extracts blender benchmark CLI"""
    download_url = "https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-3.1.0-windows.zip"
    zip_path = os.path.join(
        SCRIPT_DIR, "benchmark-launcher-cli-3.1.0-windows.zip")
    response = requests.get(download_url, allow_redirects=True, timeout=120)
    with open(zip_path, 'wb') as zip_file:
        zip_file.write(response.content)
    with ZipFile(zip_path, 'r') as zip_object:
        zip_object.extractall(path=SCRIPT_DIR)


if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    logging.info("Downloading blender benchmark CLI")
    download_and_extract_cli()


VERSION = ""
SCENE = []
DEVICE_TYPE = ""

run_array = [ABS_EXECUTABLE_PATH, "blender", "download", args.version]
process = subprocess.run(
    run_array, capture_output=True, text=True, check=False)

if process.returncode > 0:
    logging.info(process.stdout)
    logging.info(process.stderr)
    logging.error("Test failed!")

if args.scene.lower() == "all":
    SCENE = ["monster", "classroom", "junkshop"]
else:
    SCENE = [args.scene]

if args.device.lower() == "cpu":
    DEVICE_TYPE = "CPU"
else:
    run_array = [ABS_EXECUTABLE_PATH, "devices", "-b", args.version]
    process = subprocess.run(
        run_array, capture_output=True, text=True, check=False)

    if process.returncode > 0:
        logging.info(process.stdout)
        logging.info(process.stderr)
        logging.error("Test failed!")
    else:
        optix = "OPTIX"
        cuda = "CUDA"
        hip = "HIP"
        one_api = "ONEAPI"
        logging.info(process.stdout)
        logging.info(process.stderr)
        if optix in process.stdout or optix in process.stderr:
            DEVICE_TYPE = optix  # nvidia
        if cuda in process.stdout or cuda in process.stderr:
            DEVICE_TYPE = cuda  # older non rtx nvidia
        elif hip in process.stdout or hip in process.stderr:
            DEVICE_TYPE = hip  # amd
        elif one_api in process.stdout or one_api in process.stderr:
            DEVICE_TYPE = one_api  # intel

arg_string = ["blender", "list"]
run_array = [ABS_EXECUTABLE_PATH, "benchmark"] + SCENE + \
    ["-b", args.version, "--device-type", DEVICE_TYPE, "--json"]
logging.info("Running with arguments %s", run_array)
process = subprocess.run(
    run_array, capture_output=True, text=True, check=False)

if process.returncode > 0:
    logging.error(process.stderr)
    logging.error("Test failed!")

json_array = json.loads(process.stdout)

json_report = []
for report in json_array:
    blender_version = report['blender_version']['version']
    scene_report = {
        "timestamp": report['timestamp'],
        "version": blender_version,
        "test": f"{report['scene']['label']}",
        "score": round(report['stats']['samples_per_minute'], 2),
        "unit": "samples per minute",
        "device": report['device_info']['compute_devices'][0]['name']
    }

    logging.info(json.dumps(scene_report, indent=2))
    scene_report['version_json'] = report['blender_version']
    scene_report['results_json'] = report['stats']
    json_report.append(scene_report)

with open(os.path.join(log_dir, "report.json"), "w", encoding="utf-8") as file:
    file.write(json.dumps(json_report))

logging.info('Test finished!')
