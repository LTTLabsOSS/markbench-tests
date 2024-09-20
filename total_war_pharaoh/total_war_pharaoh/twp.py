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
from harness_utils.steam import get_app_install_location
from harness_utils.keras_service import KerasService

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "Pharaoh.exe"
STEAM_GAME_ID = 1937780
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
    cmd_string = f"start /D \"{get_app_install_location(STEAM_GAME_ID)}\" {PROCESS_NAME}"
    logging.info(cmd_string)
    return os.system(cmd_string)


def skip_logo_screens() -> None:
    """Simulate input to skip logo screens"""
    logging.info("Skipping logo screens")

    # Enter menu
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)


def run_benchmark(keras_service):
    """Starts the benchmark"""
    start_game()
    setup_start_time = time.time()
    time.sleep(5)

    result = keras_service.look_for_word("warning", attempts=10, interval=5)
    if not result:
        logging.info("Did not see warnings. Did the game start?")
        sys.exit(1)

    skip_logo_screens()
    time.sleep(2)

    result = keras_service.look_for_word("options", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the options menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    result = keras_service.look_for_word("bench", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the benchmark menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)
    user.press("enter")

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = keras_service.wait_for_word("fps", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = time.time() - 2

    time.sleep(90)  # Wait time for battle benchmark

    result = keras_service.wait_for_word("summary", interval=0.2, timeout=250)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = time.time() - 1

    # Wait 5 seconds for benchmark info
    time.sleep(5)

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
    keras_service = KerasService(args.keras_host, args.keras_port, LOG_DIR.joinpath("screenshot.jpg"))
    start_time, endtime = run_benchmark(keras_service)
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime)
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
