"""Atomic Heart test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
import pydirectinput as user
from utils import read_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position
from harness_utils.steam import exec_steam_run_command, get_app_install_location
from harness_utils.misc import remove_files
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.keras_service import KerasService
#pylint: enable=wrong-import-position

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\AtomicHeart\\Saved\\Config\\WindowsNoEditor"
CONFIG_FILENAME = "GameUserSettings.ini"
PROCESS_NAME = "AtomicHeart"
STEAM_GAME_ID = 668580
VIDEO_PATH = os.path.join(
    get_app_install_location(STEAM_GAME_ID), "AtomicHeart", "Content", "Movies")

skippable = [
    os.path.join(VIDEO_PATH, "Launch_4k_60FPS_PS5.mp4"),
    os.path.join(VIDEO_PATH, "Launch_4k_60FPS_XboxXS.mp4"),
    os.path.join(VIDEO_PATH, "Launch_FHD_30FPS_PS4.mp4"),
    os.path.join(VIDEO_PATH, "Launch_FHD_30FPS_XboxOne.mp4"),
    os.path.join(VIDEO_PATH, "Launch_FHD_60FPS_PC_Steam.mp4")
]

user.FAILSAFE = False


def run_benchmark():
    """Starts the benchmark"""
    remove_files(skippable)
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = time.time()

    time.sleep(10)

    result = kerasService.wait_for_word("press", timeout=25)
    if not result:
        logging.info("Did not see start screen")
        sys.exit(1)

    user.press("space")

    result = kerasService.look_for_word("continue", attempts=20, interval=1)
    if result:
        logging.info("Continue option available, navigating accordingly.")
        user.press("s")
        time.sleep(0.5)
        user.press("d")
        time.sleep(0.5)
        user.press("f")
        time.sleep(0.5)
        user.press("space")
    else:
        logging.info("Continue option not available, navigating accordingly.")
        user.press("d")
        time.sleep(0.5)
        user.press("f")
        time.sleep(0.5)
        user.press("space")

    time.sleep(10)

    result = kerasService.wait_for_word("continue", interval=1, timeout=80)
    if not result:
        logging.info("Did not see the option to continue. Check settings and try again.")
        sys.exit(1)

    logging.info("Continue found. Continuing Run.")
    user.press("space")
    time.sleep(5)

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    test_start_time = time.time()

    time.sleep(230)  # wait for No Rest For the Wicked Quest

    result = kerasService.wait_for_word("wicked", interval=1, timeout=250)
    if not result:
        logging.info(
            "Wicked was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    logging.info("Wicked found. Ending Benchmark.")
    time.sleep(5)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

parser = ArgumentParser()
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(
    LOG_DIRECTORY, "screenshot.jpg"))

try:
    start_time, end_time = run_benchmark()
    height, width = read_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
#pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
