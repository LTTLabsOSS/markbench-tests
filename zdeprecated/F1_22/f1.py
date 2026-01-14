"""F1 22 Test script"""
import logging
import sys
import os.path
import time
import pydirectinput as user
from f1_22_utils import get_args
from f1_22_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.ocr_service import OCRService
from harness_utils.steam import exec_steam_run_command, get_steamapps_common_path
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.misc import remove_files
from harness_utils.process import terminate_processes

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_GAME_ID = 1692250
VIDEO_PATH = os.path.join(get_steamapps_common_path(), "videos")

intro_videos = [
    os.path.join(VIDEO_PATH, "attract.bk2"),
    os.path.join(VIDEO_PATH, "cm_f1_sting.bk2"),
]


def navigate_overlay():
    """Simulate inputs to navigate in-game overlay."""
    # if steam in-game overlay is disabled it will be a an okay to press
    if kerasService.look_for_word("okay", attempts=5, interval=1):
        user.press("enter")
    # if steam in-game overlay is enabled we have to press escape and enter
    elif kerasService.look_for_word("please", attempts=5, interval=1):
        user.press("esc")
        time.sleep(0.5)
        user.press("down")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)

    time.sleep(3)


def navigate_menu():
    """Simulate inputs to navigate to benchmark option."""
    # Enter options
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(0.5)

    # Enter settings
    user.press("enter")
    time.sleep(0.5)

    # Enter graphics settings
    user.press("right")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(0.5)

    # Enter benchmark options
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")

    # Run benchmark!
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


def run_benchmark():
    """Runs the actual benchmark."""
    setup_start_time = time.time()
    remove_files(intro_videos)
    exec_steam_run_command(STEAM_GAME_ID)

    time.sleep(20)

    # press space through the warnings
    for _ in range(5):
        user.press("space")
        time.sleep(1)

    navigate_overlay()

    result = kerasService.look_for_word("options", attempts=5, interval=1)
    if not result:
        print("Didn't land on the main menu!")
        sys.exit(1)

    navigate_menu()

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    test_start_time = time.time()

    # sleep 3 laps
    time.sleep(330)

    navigate_overlay()

    result = kerasService.wait_for_word("results", timeout=10)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    terminate_processes("F1")
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

args = get_args()
kerasService = OCRService(args.keras_host, args.keras_port)

try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes("F1")
    sys.exit(1)
