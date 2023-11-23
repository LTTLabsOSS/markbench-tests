"""Cyberpunk 2077 test script"""
import time
import logging
import sys
import os
import pyautogui as gui
import pydirectinput as user
from cyberpunk_utils import copy_no_intro_mod, get_args, read_current_resolution


sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.keras_service import KerasService
from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game

STEAM_GAME_ID = 1091500
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "cyberpunk2077.exe"


def start_game():
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["--launcher-skip", "-skipStartScreen"])


def navigate_main_menu() -> None:
    """Simulate inputs to navigate the main menu"""
    logging.info("Navigating main menu")
    result = kerasService.look_for_word("continue", attempts=10)
    if not result:
        # an account with no save game has less menu options, so just press left and enter settings
        user.press("left")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)
        user.press("3")
        time.sleep(0.5)
        user.press("3")
        time.sleep(0.5)
        user.press("3")
        time.sleep(0.5)
        user.press("b")
    else:
        user.press("left")
        time.sleep(0.5)
        user.press("down")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)
        user.press("3")
        time.sleep(0.5)
        user.press("3")
        time.sleep(0.5)
        user.press("3")
        time.sleep(0.5)
        user.press("b")


def run_benchmark():
    """Start the benchmark"""
    copy_no_intro_mod()

    # Start game via Steam and enter fullscreen mode
    setup_start_time = time.time()
    start_game()

    time.sleep(10)

    result = kerasService.wait_for_word("new", interval=3, timeout=60)
    if not result:
        logging.info("Did not see settings menu option.")
        sys.exit(1)

    navigate_main_menu()

    # Start the benchmark!
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    test_start_time = time.time()

    result = kerasService.wait_for_word("fps", timeout=60, interval=1)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(70)
    result = kerasService.wait_for_word("results", timeout=240, interval=3)
    if not result:
        logging.info("Did not see results screen. Mark as DNF.")
        sys.exit(1)

    test_end_time = time.time()
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    gui.screenshot(os.path.join(LOG_DIRECTORY, "results.png"))
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

args = get_args()
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(
    LOG_DIRECTORY, "screenshot.jpg"))

try:
    start_time, end_time = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
