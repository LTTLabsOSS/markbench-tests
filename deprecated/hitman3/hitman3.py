"""Hitman 3 test script"""
import os
import logging
import time
import sys
from subprocess import Popen
import pyautogui as gui

from hitman_3_utils import get_resolution, wait_for_image

sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position
from harness_utils.logging import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as STEAM_PATH
#pylint: enable=wrong-import-position

STEAM_GAME_ID = 1659040
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_EXECUTABLE = "steam.exe"
PROCESS_NAMES = ['HITMAN3.exe', 'Launcher.exe']


def start_game():
    """Starts the game process"""
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info("%s %s", STEAM_PATH, steam_run_arg)
    return Popen([STEAM_PATH, steam_run_arg])


def run_benchmark():
    """Starts the benchmark"""
    setup_start_time = time.time()
    start_game()

    options_image = os.path.dirname(os.path.realpath(__file__)) + "/images/hitman3_options.png"
    options_loc = wait_for_image(options_image, 0.7, 1, 15)
    print(f"Options button is here {options_loc}")
    click_me = gui.center(options_loc)
    print(f"Center of options button is here {click_me}")
    gui.click(click_me.x, click_me.y)

    time.sleep(2)
    gui.scroll(-1000)
    time.sleep(2)

    start_image = os.path.dirname(os.path.realpath(__file__)) + "/images/start_benchmark.png"
    start_loc = wait_for_image(start_image, 0.7, 1, 10)
    print(f"Start button is here {start_loc}")
    click_me = gui.center(start_loc)
    print(f"Center of start button is here {click_me}")
    gui.click(click_me.x, click_me.y)

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    test_start_time = time.time()

    hitman_title = os.path.dirname(os.path.realpath(__file__)) + "/images/hitman_header.png"
    time.sleep(150) # sleep during benchmark 140 + 10 seconds loading.
    result = wait_for_image(hitman_title, 0.7, 2, 60)
    if not result:
        logging.error("Benchmark failed to complete! Could not find end image")
        sys.exit(1)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(*PROCESS_NAMES)
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

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
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
    terminate_processes(*PROCESS_NAMES)
    sys.exit(1)
