"""Tiny Tina's Wonderland test script"""
import logging
import time
import os
from subprocess import Popen
import sys
from utils import read_resolution, try_install_paths, get_local_drives, templates

sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position
import deprecated.cv2_utils
from harness_utils.logging import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as steam_path 
#pylint: disable=wrong-import-position

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_GAME_ID = 1286680
EXECUTABLE = "Wonderlands.exe"


def start_game() -> any:
    """Start the game process"""
    game_process = None
    try:
        exec_path = try_install_paths(get_local_drives())
        game_process = Popen(exec_path)
    except ValueError:
        logging.info("Could not find executable, trying a steam launch")

    if game_process is None:
        steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
        logging.info("%s %s", steam_path, steam_run_arg)
        game_process = Popen([steam_path, steam_run_arg])


def run_benchmark():
    """Start the benchmark"""
    start_game()
    setup_start_time = time.time()

    # wait for menu to load
    time.sleep(30)

    deprecated.cv2_utils.wait_and_click(
        "options", "options menu", deprecated.cv2_utils.ClickType.HARD)
    deprecated.cv2_utils.wait_and_click(
        "benchmark", "benchmark menu", deprecated.cv2_utils.ClickType.HARD)
    deprecated.cv2_utils.wait_and_click(
        "start", "start benchmark", deprecated.cv2_utils.ClickType.HARD)
    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    test_start_time = time.time()

    time.sleep(124)
    deprecated.cv2_utils.wait_for_image_on_screen("options", 0.8, 2, 60)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes("Wonderlands")
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

try:
    deprecated.cv2_utils.templates = templates
    start_time, end_time = run_benchmark()
    height, width = read_resolution()
    result = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
#pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes("Wonderlands")
    sys.exit(1)
