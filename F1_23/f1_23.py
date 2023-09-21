"""F1 23 test script"""
import logging
from argparse import ArgumentParser
import os.path
import time
import sys
import pydirectinput as user
from f1_23_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], ".."))

# pylint: disable=wrong-import-position
from harness_utils.steam import exec_steam_run_command, get_app_install_location
from harness_utils.keras_service import KerasService
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
# pylint: enable=wrong-import-position

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "F1_23"
STEAM_GAME_ID = 2108330
VIDEO_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "videos")

skippable = [
    os.path.join(VIDEO_PATH, "attract.bk2"),
    os.path.join(VIDEO_PATH, "cm_f1_sting.bk2")
]


def is_word_on_screen(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    """Sends screenshot to Keras service to search for a given word a specified number of times"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result is not None:
            return True
        time.sleep(delay_seconds)
    return False


def official() -> any:
    """Look for product"""
    return is_word_on_screen(word="product", attempts=20, delay_seconds=0.5)


def press() -> any:
    """Look for press"""
    return is_word_on_screen(word="press", attempts=40, delay_seconds=2)


def login() -> any:
    """Look for login"""
    return is_word_on_screen(word="login", attempts=100, delay_seconds=0.2)


def benchmark_start() -> any:
    """Look for lap"""
    return is_word_on_screen(word="lap", attempts=15, delay_seconds=3)


def results() -> any:
    """Look for results"""
    return is_word_on_screen(word="results", attempts=20, delay_seconds=3)


def menu() -> any:
    """Look for theatre"""
    return is_word_on_screen(word="theatre", attempts=5, delay_seconds=3)


def find_settings() -> any:
    """Look for and enter settings"""
    if not is_word_on_screen(word="settings", attempts=5, delay_seconds=3):
        logging.info("Didn't find settings!")
        sys.exit(1)
    user.press("enter")
    time.sleep(1.5)


def find_graphics() -> any:
    """Look for and enter graphics settings"""
    if not is_word_on_screen(word="graphics", attempts=5, delay_seconds=3):
        logging.info("Didn't find graphics!")
        sys.exit(1)
    user.press("right")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1.5)


def find_benchmark() -> any:
    """Look for and enter benchmark options"""
    if not is_word_on_screen(word="benchmark", attempts=5, delay_seconds=3):
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
    if not is_word_on_screen(word="weather", attempts=5, delay_seconds=3):
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
    start_game_screen = time.time()
    while True:
        if official():
            logging.info("Game started. Skipping intros.")
            user.press("space")
            time.sleep(1)
            user.press("space")
            time.sleep(1)
            user.press("space")
            time.sleep(4)
            break
        if time.time() - start_game_screen > 60:
            logging.info(
                "Game didn't start in time. Check settings and try again.")
            sys.exit(1)
        logging.info("Game hasn't started. Trying again in 5 seconds")
        time.sleep(5)

    # Press enter to proceed to the main menu
    start_game_screen = time.time()
    while True:
        if press():
            logging.info("Hit the title screen. Continuing")
            user.press("enter")
            time.sleep(1)
            break
        if time.time() - start_game_screen > 60:
            logging.info(
                "Game didn't start in time. Check settings and try again.")
            sys.exit(1)
        logging.info("Game hasn't started. Trying again in 5 seconds")
        time.sleep(5)

    # cancel logging into ea services
    if login():
        logging.info("Cancelling logging in.")
        user.press("enter")
        time.sleep(2)


def navigate_menu():
    """Simulate inputs to navigate to benchmark option."""
    menu_screen = time.time()
    while True:
        if menu():
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
            break
        if time.time() - menu_screen > 60:
            logging.info("Didn't land on the main menu!")
            sys.exit(1)
        logging.info("Game still loading. Trying again in 10 seconds")
        time.sleep(10)

    find_settings()
    find_graphics()
    find_benchmark()
    find_weather() # Run benchmark!

def run_benchmark():
    """Runs the actual benchmark."""
    remove_files(skippable)
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = time.time()
    time.sleep(2)
    navigate_startup()
    navigate_menu()

    loading_screen_start = time.time()
    while True:
        if benchmark_start():
            test_start_time = time.time()
            logging.info(
                "Benchmark started. Waiting for benchmark to complete.")
            break
        if time.time() - loading_screen_start > 60:
            logging.info("Benchmark didn't start.")
            sys.exit(1)
        logging.info("Benchmark hasn't started. Trying again in 10 seconds")
        time.sleep(10)

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    # sleep for 3 laps
    time.sleep(350)

    results_screen_start = time.time()
    while True:
        if results():
            logging.info("Results screen was found! Finishing benchmark.")
            break
        if time.time() - results_screen_start > 60:
            logging.info("Results screen was not found!" +
                "Did harness not wait long enough? Or test was too long?")
            sys.exit(1)
        logging.info("Benchmark hasn't finished. Trying again in 10 seconds")
        time.sleep(10)

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
    args.keras_host, args.keras_port, os.path.join(
        LOG_DIRECTORY, "screenshot.jpg")
)

try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "graphics_preset": "current",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)

#pylint: disable=broad-exception-caught

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
