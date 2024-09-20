"""Grid Legends test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import re
import time
import pydirectinput as user
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

#pylint: disable=wrong-import-position
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

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "gridlegends.exe"
STEAM_GAME_ID = 1307710


def get_resolution() -> tuple[int]:
    """Gets resolution width and height from local xml file created by game."""
    username = os.getlogin()
    config_path = f"C:\\Users\\{username}\\Documents\\My Games\\GRID Legends\\hardwaresettings"
    config_filename = "hardware_settings_config.xml"
    resolution = re.compile(r"<resolution width=\"(\d+)\" height=\"(\d+)\"")
    cfg = f"{config_path}\\{config_filename}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = resolution.search(line)
            width_match = resolution.search(line)
            if height_match is not None:
                height = height_match.group(2)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)


def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()


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
    """Launch the game"""
    return exec_steam_game(STEAM_GAME_ID)


def run_benchmark(keras_service):
    """Run Grid Legends benchmark"""
    setup_start_time = time.time()
    start_game()
    time.sleep(20)  # wait for game to load to the start screen

    if keras_service.wait_for_word(word="press", timeout=80, interval=1) is None:
        logging.error("Game didn't load to start screen. Did the game load?")
        sys.exit(1)

    logging.info('Game started. Entering main menu')
    time.sleep(2)
    user.press("enter")
    time.sleep(2)

    # waiting about a minute for the main menu to appear
    if keras_service.wait_for_word(word="home", timeout=80, interval=1) is None:
        logging.error("Game didn't load to main menu. Check settings and try again.")
        sys.exit(1)

    logging.info('Starting benchmark')
    user.press("f3")
    time.sleep(0.2)
    user.press("right")
    time.sleep(0.2)
    user.press("right")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)

    if keras_service.wait_for_word(word="basic", timeout=30, interval=0.1) is None:
        logging.error("Didn't basic video options. Did the menu navigate correctly?")
        sys.exit(1)

    user.press("f3")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)

    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    if keras_service.wait_for_word(word="manzi", timeout=30, interval=0.1) is None:
        logging.error("Didn't see Valentino Manzi. Did the benchmark load?")
        sys.exit(1)
    test_start_time = time.time()

    time.sleep(136)
    # TODO -> Mark benchmark start time using video OCR by looking for a players name
    if keras_service.wait_for_word(word="results", timeout=30, interval=0.1) is None:
        logging.error("Didn't see results screen for the bnechmark. Could not mark start time! Did the benchmark crash?")
        sys.exit(1)

    test_end_time = time.time() - 2
    time.sleep(2)

    logging.info("Run completed. Closing game.")
    time.sleep(2)
    return test_start_time, test_end_time



try:
    args = get_args()
    keras_service = KerasService(args.keras_host, args.keras_port, LOG_DIR.joinpath("screenshot.jpg"))
    start_time, end_time = run_benchmark(keras_service)
    elapsed_test_time = round((end_time - start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(PROCESS_NAME)
    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIR, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)

if __name__ == "__main__":
    try:
        setup_logging()
        run_benchmark()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
