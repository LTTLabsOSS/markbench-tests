import time
import pydirectinput as user
import pyautogui as gui
import logging
from pywinauto import mouse
from win32con import SM_CXSCREEN, SM_CYSCREEN
import win32api
from subprocess import Popen
import sys
import os
import shutil
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.keras_service import KerasService
from harness_utils.logging import setup_log_directory, write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as STEAM_PATH
from utils import copy_no_intro_mod, get_args, read_current_resolution


STEAM_GAME_ID = 1091500
STEAM_PATH = os.path.join(os.environ["ProgramFiles(x86)"], "steam")
STEAM_EXECUTABLE = "steam.exe"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "cyberpunk2077.exe"


# Launch the game with no launcher or start screen
def start_game():
    cmd = os.path.join(STEAM_PATH, STEAM_EXECUTABLE)
    cmd_array = [cmd, "-applaunch",
                 str(STEAM_GAME_ID), "--launcher-skip", "-skipStartScreen"]
    logging.info(" ".join(cmd_array))
    return Popen(cmd_array)


def is_word_present(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result != None:
            return True
        time.sleep(delay_seconds)
    return False


def await_settings_menu() -> any:
    return is_word_present(word="new", attempts=20, delay_seconds=3)


def await_results_screen() -> bool:
    return is_word_present(word="results", attempts=10, delay_seconds=3)


def await_benchmark_start() -> bool:
    return is_word_present(word="fps", attempts=10, delay_seconds=2)


def is_continue_present() -> bool:
    return is_word_present(word="continue", attempts=10)


def navigate_main_menu() -> None:
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
    copy_no_intro_mod()

    """
    Start game via Steam and enter fullscreen mode
    """
    t1 = time.time()
    game_process = start_game()
    time.sleep(10)

    settings_menu_screen = await_settings_menu()

    if not settings_menu_screen:
        logging.info("Did not see settings menu option.")
        exit(1)

    navigate_main_menu()

    # """
    # Start the benchmark!
    # """
    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")

    global START_TIME
    START_TIME = time.time()

    # Checking if loading screen is finished
    benchmark_started = False

    loading_screen_start = time.time()
    logging.info(f"Looking for fps counter to indicate benchmark started")
    while (not benchmark_started):
        if time.time()-loading_screen_start > 60:
            logging.info("Benchmark didn't start.")
            exit(1)
        benchmark_started = await_benchmark_start()

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    
    # """
    # Wait for benchmark to complete
    # """
    time.sleep(70)
    logging.info(f"Finished sleeping, waiting for results screen")
    count = 0
    results_screen_present = False
    while (not results_screen_present):
           results_screen_present = await_results_screen()
           if results_screen_present:
               break # break out early if we found it
           if count >= 3: # we check 3 times every 40 minnutes because lower end cards take *forever* to finish
                logging.info("Did not see results screen. Mark as DNF.")
                exit(1)
           logging.info(f"Benchmark not finished yet, continuing to wait for the {count} time")
           time.sleep(40)
           count += 1

    global END_TIME
    END_TIME = time.time()

    logging.info(f"Benchmark took {round((END_TIME - START_TIME), 2)} seconds")
    gui.screenshot(os.path.join(LOG_DIRECTORY, "results.png"))
    terminate_processes(PROCESS_NAME)
    return START_TIME, END_TIME


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
    result = {
        "resolution": f"{resolution}",
        "graphics_preset": "current",
        "start_time": round((start_time * 1000)),  # seconds * 1000 = millis
        "end_time": round((endtime * 1000))
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    exit(1)
