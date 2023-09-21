"""The Last of Us Part I test script"""
import logging
import os
import time
import sys
import pydirectinput as user
import pyautogui as gui

from the_last_of_us_part_i_utils import get_args, get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position
from harness_utils.keras_service import KerasService
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
  get_registry_active_user,
  exec_steam_run_command,
)
#pylint: enable=wrong-import-position

STEAM_GAME_ID = 1888930
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "tlou"

user.FAILSAFE = False


def await_start_screen(attempts: int) -> bool:
    """Wait for the start menu"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("press")
        if result is not None:
            return True
        time.sleep(5)

    return False


def navigate_main_menu() -> None:
    """Input to navigate main menu"""
    logging.info("Navigating main menu")

    # Enter TLOU menu
    user.press("space")
    time.sleep(0.5)
    user.press("space")
    time.sleep(0.5)

    # Press load game
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.keyDown("space")
    time.sleep(0.5)

    # Go to bottom save
    user.press("up")
    time.sleep(0.5)
    user.press("space")
    time.sleep(0.5)
    user.press("space")
    time.sleep(2)


def await_load_game_menu(attempts: int) -> any:
    """Wait for load game menu"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("yes")
        if result is not None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def await_fromy(attempts: int) -> bool:
    """Wait for "from? in dialogue subtitles"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("fromy")
        if result is not None:
            logging.info("Fromy found!!!")
            return True
        time.sleep(0.1)

    return False


def run_benchmark():
    """Starts the benchmark"""
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = time.time()

    time.sleep(10)

    start_screen_found = await_start_screen(10)

    if not start_screen_found:
        logging.info("Did not see start screen")
        sys.exit(1)

    navigate_main_menu()

    # press load save
    coords = await_load_game_menu(10)

    if not coords:
        logging.info("Did not load the save")
        sys.exit(1)

    user.click(coords[0], coords[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    test_start_time = time.time()

    time.sleep(150) # wait for black screen

    # This actually looks for "from?" but the current ML model sees it as fromy
    fromy_found = await_fromy(250)

    if not fromy_found:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    # Wait for black screen
    time.sleep(24)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

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
kerasService = KerasService(
    args.keras_host, args.keras_port, os.path.join(LOG_DIRECTORY, "screenshot.jpg"))

try:
    start_time, end_time = run_benchmark()
    steam_id = get_registry_active_user()
    config_path = os.path.join(
        os.environ["HOMEPATH"], "Saved Games" ,"The Last of Us Part I",
        "users", str(steam_id), "screeninfo.cfg"
    )
    height, width = get_resolution(config_path)
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
