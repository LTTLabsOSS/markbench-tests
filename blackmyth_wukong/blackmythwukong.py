"""Total War: Warhammer III test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import re
import pyautogui as gui
import pydirectinput as user

sys.path.insert(1, os.path.join(sys.path[0], '..'))

#pylint: disable=wrong-import-position
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.steam import get_app_install_location, get_build_id, exec_steam_game
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import clickme

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "b1-Win64-Shipping.exe"
STEAM_GAME_ID = 3132990
APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Pharaoh\\scripts"
CONFIG_FILENAME = "preferences.script.txt"

user.FAILSAFE = False


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"y_res (\d+);")
    width_pattern = re.compile(r"x_res (\d+);")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


def start_game():
    """Starts the game process"""
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")

def run_benchmark(keras_service):
    """Starts the benchmark"""
    start_game()
    setup_start_time = time.time()
    am = ArtifactManager(LOG_DIR)
    time.sleep(30)

    if keras_service.wait_for_word(word="black", timeout=30, interval=1) is None:
        logging.info("Did not find the welcome screen. Did the game launch correctly?")
        sys.exit(1)

    time.sleep(2)
    user.press("space")
    time.sleep(2)
    # sys.exit(1)

    result = keras_service.look_for_word("benchmark", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the option to start the benchmark. Did the game exit the settings menu correctly?")
        sys.exit(1)

    clickme(result["x"], result["y"])
    time.sleep(2)
    user.press("enter")
    time.sleep(2)
    result = keras_service.wait_for_word("current", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find current. Unable to mark start time!")
        sys.exit(1)

    test_start_time = time.time() - 2

    time.sleep(142)

    if keras_service.wait_for_word(word="result", timeout=30, interval=1) is None:
        logging.info("Did not find result screen. Did the benchmark run?")
        sys.exit(1)

    test_end_time = time.time() - 1
    time.sleep(5)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    time.sleep(0.5)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


def setup_logging():
    """setup logging"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=f'{LOG_DIR}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def main():
    """entry point"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    keras_service = KerasService(args.keras_host, args.keras_port)
    start_time, endtime = run_benchmark(keras_service)
    # height, width = read_current_resolution()
    # report = {
    #     "resolution": format_resolution(width, height),
    #     "start_time": seconds_to_milliseconds(start_time),
    #     "end_time": seconds_to_milliseconds(endtime),
    #     "version": get_build_id(STEAM_GAME_ID)
    # }

    #write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
