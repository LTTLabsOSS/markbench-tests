"""Stellaris test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import pyautogui as gui
import pydirectinput as user

from stellaris_utils import read_current_resolution, copy_benchmarkfiles, copy_benchmarksave, find_score_in_log

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.steam import get_app_install_location
from harness_utils.keras_service import KerasService


SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "stellaris.exe"
STEAM_GAME_ID = 281990

user.FAILSAFE = False


def setup_logging():
    """default logging config"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=f'{LOG_DIR}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def start_game():
    """Starts the game process"""
    cmd_string = f"start /D \"{get_app_install_location(STEAM_GAME_ID)}\" {PROCESS_NAME}"
    logging.info(cmd_string)
    return os.system(cmd_string)


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")


def run_benchmark(keras_host, keras_port):
    """Starts the benchmark"""
    keras_service = KerasService(keras_host, keras_port)
    copy_benchmarkfiles()
    copy_benchmarksave()
    start_game()
    setup_start_time = int(time.time())
    time.sleep(5)

    result = keras_service.wait_for_word("credits", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the paused notification. Unable to mark start time!")
        sys.exit(1)

    result = keras_service.look_for_word("load", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the load save menu. Is there something wrong on the screen?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    result = keras_service.wait_for_word("paused", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the paused notification. Unable to mark start time!")
        sys.exit(1)

    result = keras_service.look_for_word("government", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the load latest save button. Did keras click correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])

    time.sleep(2)
    logging.info('Starting benchmark')
    user.press("`")
    time.sleep(0.5)
    console_command("run benchmark.ini")
    time.sleep(1)

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    test_start_time = int(time.time())
    time.sleep(30)

    result = keras_service.wait_for_word("finished", interval=0.2, timeout=250)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = int(time.time())

    # Wait 5 seconds for benchmark info
    time.sleep(10)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    score = find_score_in_log()
    logging.info("The one year passed in %s seconds", score)
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time, score


def main():
    """entry point to test script"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()

    test_start_time, test_end_time, score = run_benchmark(args.keras_host, args.keras_port)
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "test": "Stellaris",
        "unit": "Seconds",
        "score": score
    }

    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
