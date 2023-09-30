#!/usr/bin/env python3

"""Counter Strike: Global Offensive test script"""
import logging
import os
import time
import sys
from argparse import ArgumentParser
import pyautogui as gui
try:
    import pydirectinput as user
except ImportError:
    import pyautogui as user
from utils import (
    get_resolution,
    benchmark_folder_exists,
    download_benchmark,
    copy_benchmark,
    STEAM_GAME_ID
)

sys.path.insert(1, os.path.join(sys.path[0], '..'))

# pylint: disable=wrong-import-position
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_run_command
from harness_utils.keras_service import KerasService
# pylint: enable=wrong-import-position

MAP = "de_dust2"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "csgo.exe"


def console_command(command):
    """Types out the provided command one character at a time"""
    for char in command:
        gui.press(char)
    user.press("enter")


def run_benchmark():
    """Start the benchmark"""
    if not benchmark_folder_exists():
        download_benchmark()

    copy_benchmark()
    setup_start_time = time.time()
    exec_steam_run_command(STEAM_GAME_ID)
    time.sleep(30)  # wait for game to load into main menu

    logging.info("Waiting for game to start...")
    result = kerasService.wait_for_word("news", interval=2, timeout=120)
    if not result:
        logging.info("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    logging.info('Game started. Loading map.')
    user.press("`")
    time.sleep(1)
    console_command(f"map {MAP}")
    time.sleep(5)  # wait for map to load

    logging.info("Waiting for map to load...")
    result = kerasService.wait_for_word("terrorists", interval=2, timeout=120)
    if not result:
        logging.info("Game didn't load map. Check settings and try again.")
        sys.exit(1)

    logging.info('Map loaded. Starting benchmark.')
    time.sleep(1)
    user.press("`")
    time.sleep(0.5)
    console_command("exec benchmark")
    time.sleep(0.5)
    console_command("benchmark")

    elapsed_setup_time = round((time.time() - setup_start_time), 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)
    test_start_time = time.time()

    logging.info("Waiting for benchmark to run...")
    time.sleep(43) #approximate wait time

    logging.info("Waiting for benchmark results...")
    result = kerasService.wait_for_word("finished", interval=1, timeout=60)
    if not result:
        logging.info("Game didn't finish. Check settings and try again.")
        sys.exit(1)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)
    return start_time, end_time


# Entry Point
setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

parser = ArgumentParser()
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(
    LOG_DIRECTORY, "screenshot.jpg"))

benchmark_folder_exists()
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
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
