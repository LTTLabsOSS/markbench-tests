"""Cyberpunk 2077 test script"""
import time
import logging
from subprocess import Popen
import sys
import os
from cyberpunk_utils import copy_no_intro_mod, get_args, read_current_resolution
import pyautogui as gui
import pydirectinput as user


sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position
from harness_utils.keras_service import KerasService
from harness_utils.output import (
    setup_log_directory, write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.steam import DEFAULT_EXECUTABLE_PATH as STEAM_PATH
#pylint: enable=wrong-import-position

STEAM_GAME_ID = 1091500
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "cyberpunk2077.exe"


def start_game():
    """Launch the game with no launcher or start screen"""
    cmd_array = [STEAM_PATH, "-applaunch",
                 str(STEAM_GAME_ID), "--launcher-skip", "-skipStartScreen"]
    logging.info(" ".join(cmd_array))
    return Popen(cmd_array)


def is_word_present(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    """Find given word on screen"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result is not None:
            return True
        time.sleep(delay_seconds)
    return False


def await_settings_menu() -> any:
    """Wait for word "new" on screen"""
    return is_word_present(word="new", attempts=20, delay_seconds=3)


def await_results_screen() -> bool:
    """Wait for word "results" on screen"""
    return is_word_present(word="results", attempts=10, delay_seconds=3)


def await_benchmark_start() -> bool:
    """Wait for word "fps" on screen"""
    return is_word_present(word="fps", attempts=10, delay_seconds=2)


def is_continue_present() -> bool:
    """Wait for word "continue" on screen"""
    return is_word_present(word="continue", attempts=10)


def navigate_main_menu() -> None:
    """Simulate inputs to navigate the main menu"""
    logging.info("Navigating main menu")
    continue_present = is_continue_present()
    if not continue_present:
        # an account with no save game has less menu options, so just press left and enter settings
        user.press("left")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)
        user.press("b")
    else:
        user.press("left")
        time.sleep(0.5)
        user.press("down")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)
        user.press("b")


def run_benchmark():
    """Start the benchmark"""
    copy_no_intro_mod()

    # Start game via Steam and enter fullscreen mode
    setup_start_time = time.time()
    start_game()
    time.sleep(10)

    settings_menu_screen = await_settings_menu()

    if not settings_menu_screen:
        logging.info("Did not see settings menu option.")
        sys.exit(1)

    navigate_main_menu()

    # Start the benchmark!
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    test_start_time = time.time()

    # Checking if loading screen is finished
    benchmark_started = False

    loading_screen_start = time.time()
    logging.info("Looking for fps counter to indicate benchmark started")
    while not benchmark_started:
        if time.time()-loading_screen_start > 60:
            logging.info("Benchmark didn't start.")
            sys.exit(1)
        benchmark_started = await_benchmark_start()

    logging.info("Benchmark started. Waiting for benchmark to complete.")

    # Wait for benchmark to complete
    time.sleep(70)
    logging.info("Finished sleeping, waiting for results screen")
    count = 0
    results_screen_present = False
    while not results_screen_present:
        results_screen_present = await_results_screen()
        if results_screen_present:
            break
        # we check 3 times every 40 minutes because lower end cards take *forever* to finish
        if count >= 3:
            logging.info("Did not see results screen. Mark as DNF.")
            sys.exit(1)
        logging.info("Benchmark not finished yet, continuing to wait for the %d time", count)
        time.sleep(40)
        count += 1

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
    start_time, endtime = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": round((start_time * 1000)),
        "end_time": round((endtime * 1000))
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
#pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
