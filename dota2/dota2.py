"""Dota 2 test script"""
import logging
import os
import time
import pydirectinput as user
import sys
from dota2_utils import console_command, get_resolution, copy_replay, copy_config, get_args

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.steam import exec_steam_game


SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "dota2.exe"
STEAM_GAME_ID = 570

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

def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-console", "+fps_max 0"])

def run_benchmark():
    """Run dota2 benchmark"""
    copy_replay()
    copy_config()
    setup_start_time = time.time()
    start_game()
    time.sleep(10)  # wait for game to load into main menu

    # to skip logo screen
    if kerasService.wait_for_word(word="va", timeout=20, interval=1):
        logging.info('Game started. Entering main menu')
        user.press("esc")
        time.sleep(1)

    # waiting about a minute for the main menu to appear
    if kerasService.wait_for_word(word="heroes", timeout=80, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    logging.info('Starting benchmark')
    user.press("\\")
    time.sleep(0.2)
    console_command("exec_async benchmark")
    time.sleep(0.2)
    user.press("\\")
    time.sleep(5)

    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    test_start_time = time.time()

    # TODO -> Mark benchmark start time using video OCR by looking for a players name
    if kerasService.wait_for_word(word="directed", timeout=100, interval=0.5) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    time.sleep(100) # sleep duration during gameplay

    if kerasService.wait_for_word(word="heroes", timeout=25, interval=1) is None:
        logging.error("Main menu after running benchmark not found, exiting")
        sys.exit(1)

    logging.info("Run completed. Closing game.")
    test_end_time = time.time()

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
