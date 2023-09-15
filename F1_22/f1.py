"""F1 22 Test script"""
import logging
import sys
import os.path
import time
from subprocess import Popen
import pydirectinput as user
from f1_22_utils import get_args
from f1_22_utils import get_resolution, remove_intro_videos

sys.path.insert(1, os.path.join(sys.path[0], ".."))

#pylint: disable=wrong-import-position

from harness_utils.keras_service import KerasService
from harness_utils.logging import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes

#pylint: enable=wrong-import-position

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_GAME_ID = 1692250
STEAM_PATH = os.path.join(os.environ["ProgramFiles(x86)"], "steam")
STEAM_EXECUTABLE = "steam.exe"
VIDEO_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\F1 22\videos"

skippable = [
    os.path.join(VIDEO_PATH, "attract.bk2"),
    os.path.join(VIDEO_PATH, "cm_f1_sting.bk2"),
]


def wait_for_word(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    """Gets results of search for word in screenshot sent to Keras Service."""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result is not None:
            return True
        time.sleep(delay_seconds)
    return False


def start_game():
    """Starts the game via steam command."""
    steam_run_arg = "steam://rungameid/" + str(STEAM_GAME_ID)
    start_cmd = STEAM_PATH + "\\" + STEAM_EXECUTABLE
    logging.info("%s %s", start_cmd, steam_run_arg)
    return Popen([start_cmd, steam_run_arg])


def navigate_overlay():
    """Simulate inputs to navigate ingame overlay."""
    # if steam ingame overlay is disabled it will be a an okay to press
    okay_present = wait_for_word(word="okay", attempts=5, delay_seconds=1)
    if okay_present:
        user.press("enter")

    time.sleep(3)

    # if steam ingame overlay is enabled we have to press escape and enter
    if not okay_present:
        please_present = wait_for_word(word="please", attempts=5, delay_seconds=1)
        if please_present is not None:
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
    remove_intro_videos(skippable)
    start_game()

    time.sleep(20)

    # press space through the warnings
    for _ in range(5):
        user.press("space")
        time.sleep(1)

    navigate_overlay()

    options_present = wait_for_word("options", attempts=5, delay_seconds=1)
    if not options_present:
        print("Didn't land on the main menu!")
        sys.exit(1)

    navigate_menu()

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    test_start_time = time.time()

    # sleep 6.75 for 3 laps
    time.sleep(330)

    # if steam ingame overlay is disabled it will be a an okay to press
    okay_present = wait_for_word(word="okay", attempts=5, delay_seconds=1)
    if okay_present:
        user.press("enter")

    time.sleep(3)

    if not okay_present:
        # if steam ingame overlay is enabled we have to press escape and enter
        please_present = wait_for_word(word="please", attempts=5, delay_seconds=1)
        if please_present is not None:
            user.press("esc")
            time.sleep(0.5)
            user.press("down")
            time.sleep(0.5)
            user.press("enter")
            time.sleep(0.5)

    time.sleep(3)

    results_present = wait_for_word(word="results", attempts=5, delay_seconds=1)
    if not results_present:
        print(
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

#pylint: disable=broad-exception-caught

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes("F1")
    sys.exit(1)
