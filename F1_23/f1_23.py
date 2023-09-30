"""F1 23 test script"""
import logging
import os.path
import sys
import time
from argparse import ArgumentParser

import pydirectinput as user
from f1_23_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.keras_service import KerasService
from harness_utils.misc import remove_files
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.process import terminate_processes

# pylint: disable=wrong-import-position
from harness_utils.steam import exec_steam_run_command, get_app_install_location

# pylint: enable=wrong-import-position

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "F1_23"
STEAM_GAME_ID = 2108330
VIDEO_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "videos")

skippable = [
    os.path.join(VIDEO_PATH, "attract.bk2"),
    os.path.join(VIDEO_PATH, "cm_f1_sting.bk2"),
]


def find_settings() -> any:
    """Look for and enter settings"""
    if not kerasService.look_for_word("settings", attempts=5, interval=3):
        logging.info("Didn't find settings!")
        sys.exit(1)
    user.press("enter")
    time.sleep(1.5)


def find_graphics() -> any:
    """Look for and enter graphics settings"""
    if not kerasService.look_for_word("graphics", attempts=5, interval=3):
        logging.info("Didn't find graphics!")
        sys.exit(1)
    user.press("right")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1.5)


def find_benchmark() -> any:
    """Look for and enter benchmark options"""
    if not kerasService.look_for_word("benchmark", attempts=5, interval=3):
        logging.info("Didn't find benchmark!")
        sys.exit(1)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1.5)


def find_weather() -> any:
    """Navigate to start benchmark"""
    if not kerasService.look_for_word("weather", attempts=5, interval=3):
        logging.info("Didn't find weather!")
        sys.exit(1)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(2)


def navigate_startup():
    """press space through the warnings and navigate startup menus"""
    result = kerasService.wait_for_word("product", timeout=40)
    if not result:
        logging.info("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    user.press("space")
    time.sleep(1)
    user.press("space")
    time.sleep(1)
    user.press("space")
    time.sleep(4)

    # Press enter to proceed to the main menu
    result = kerasService.wait_for_word("press", interval=2, timeout=80)
    if not result:
        logging.info("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    logging.info("Hit the title screen. Continuing")
    user.press("enter")
    time.sleep(1)

    # cancel logging into ea services
    result = kerasService.wait_for_word("login", timeout=50)
    if result:
        logging.info("Cancelling logging in.")
        user.press("enter")
        time.sleep(2)


def navigate_menu():
    """Simulate inputs to navigate to benchmark option."""
    result = kerasService.wait_for_word("theatre", interval=3, timeout=60)
    if not result:
        logging.info("Didn't land on the main menu!")
        sys.exit(1)

    logging.info("Saw the options! we are good to go!")
    time.sleep(1)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(2)

    find_settings()
    find_graphics()
    find_benchmark()
    find_weather()  # Run benchmark!


def run_benchmark():
    """Runs the actual benchmark."""
    remove_files(skippable)
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = time.time()
    time.sleep(2)
    navigate_startup()
    navigate_menu()

    result = kerasService.wait_for_word("lap", interval=3, timeout=90)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    test_start_time = time.time()

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    # sleep for 3 laps
    time.sleep(350)

    result = kerasService.wait_for_word("results", interval=3, timeout=90)
    if not result:
        logging.info(
            "Results screen was not found!"
            + "Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    logging.info("Results screen was found! Finishing benchmark.")

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(
    filename=f"{LOG_DIRECTORY}/harness.log",
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG,
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

parser = ArgumentParser()
parser.add_argument(
    "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True
)
parser.add_argument(
    "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True
)
args = parser.parse_args()
kerasService = KerasService(
    args.keras_host, args.keras_port, os.path.join(LOG_DIRECTORY, "screenshot.jpg")
)

try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
# pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
