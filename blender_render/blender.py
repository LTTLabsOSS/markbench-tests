"""Blender render test script"""
from blender_utils import download_and_install_blender, \
    download_barbershop_scene, run_blender_render
from argparse import ArgumentParser
import logging
import os.path
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from harness_utils.output import write_report_json

MSI_NAME = "blender-3.6.4-windows-x64.msi"
DOWNLOAD_URL = f"https://mirrors.ocf.berkeley.edu/blender/release/Blender3.6/{MSI_NAME}"
ABSOLUTE_PATH = "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIR, "run")
if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)
LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=LOGGING_FORMAT,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

VALID_DEVICES = ["CPU", "CUDA", "OPTIX", "HIP", "ONEAPI", "METAL"]
parser = ArgumentParser()
parser.add_argument("-s", "--scene", dest="scene",
                    help="blender scene", metavar="scene", required=True)
parser.add_argument("-d", "--device", dest="device",
                    help="device", metavar="device", required=True)

args = parser.parse_args()

if args.device not in VALID_DEVICES:
    logging.error("Invalid device selection!")
    sys.exit(1)

if os.path.isfile(ABSOLUTE_PATH) is False:
    download_and_install_blender(DOWNLOAD_URL, MSI_NAME)

if os.path.isfile(ABSOLUTE_PATH) is False:
    logging.error("Failed to install Blender, exiting")
    sys.exit(1)

logging.info('Blender already installed')

download_barbershop_scene()

try:
    logging.info('Starting benchmark!')
    start_time = time.time()
    score = run_blender_render(
        ABSOLUTE_PATH, LOG_DIRECTORY, args.device.upper())
    end_time = time.time()
    logging.info('Finished rendering barbership in %s seconds', (end_time - start_time)/ 60)

    if score is None:
        logging.error("No duration was found in the log to use as the score")
        sys.exit(1)

    report = {
        "score": score,
        "start_time": round((start_time * 1000)),
        "end_time": round((end_time * 1000))
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
