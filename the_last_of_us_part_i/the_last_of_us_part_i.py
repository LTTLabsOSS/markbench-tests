from argparse import ArgumentParser
import logging
import os
import pydirectinput as user
import time
from subprocess import Popen
import sys
import pyautogui as gui

from the_last_of_us_part_i_utils import get_args, get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.keras_service import KerasService
from harness_utils.logging import *
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, get_registry_active_user, DEFAULT_EXECUTABLE_PATH as STEAM_PATH

STEAM_GAME_ID = 1888930 
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "tlou"

id = get_registry_active_user()
config_path = os.path.join(os.environ["HOMEPATH"], "Saved Games" ,"The Last of Us Part I", "users", str(id), "screeninfo.cfg")

user.FAILSAFE = False


def start_game():
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info(STEAM_PATH + " " + steam_run_arg)
    return Popen([STEAM_PATH, steam_run_arg])


def await_start_screen(attempts: int) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("press")
        if result != None:
            return True
        time.sleep(5)
    
    return False


def navigate_main_menu() -> None:
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
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("yes")
        if result != None:
            return (result["x"], result["y"])
        time.sleep(1)
    
    return None


def await_fromy(attempts: int) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("fromy")
        if result != None:
            logging.info("Fromy found!!!")
            return True
        time.sleep(0.1)

    return False


def run_benchmark():
    start_game()
    t1 = time.time()

    time.sleep(10)

    start_screen_found = await_start_screen(10)
    
    if not start_screen_found:
        logging.info("Did not see start screen")
        exit(1)

    navigate_main_menu()

    # press load save
    coords = await_load_game_menu(10)

    if not coords:
        logging.info("Did not load the save")
        exit(1)

    user.click(coords[0], coords[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp() 

    t2 = time.time()
    logging.info(f"Setup took {round((t2 - t1), 2)} seconds")
    start_time = time.time()

    time.sleep(150) # wait for black screen

    # This actually looks for "from?" but the current ML model sees it as fromy
    fromy_found = await_fromy(250)

    if not fromy_found:
        logging.info("Results screen was not found! Did harness not wait long enough? Or test was too long?")
        exit(1)

    # Wait for black screen
    time.sleep(24)

    # End the run
    end_time = time.time()
    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")

    # Exit
    terminate_processes(PROCESS_NAME)
    return start_time, end_time
    

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
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(LOG_DIRECTORY, "screenshot.jpg"))

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution(config_path)
    result = {
        "resolution": format_resolution(width, height),
        "graphics_preset": "current",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    exit(1)