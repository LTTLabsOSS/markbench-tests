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
from harness_utils.steam import get_app_install_location, get_build_id
from harness_utils.ocr_service import OcrService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import mouse_scroll_n_times

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
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    start_game()
    setup_start_time = int(time.time())
    am = ArtifactManager(LOG_DIR)
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

    if keras_service.wait_for_word(word="brightness", timeout=30, interval=1) is None:
        logging.info("Did not find the main menu. Did Keras click correctly?")
        sys.exit(1)

    am.take_screenshot("main.png", ArtifactType.CONFIG_IMAGE, "screenshot of main settings menu")
    time.sleep(0.5)

    result = keras_service.look_for_word("advanced", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the advanced options menu. Did the game navigate to options correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    if keras_service.wait_for_word(word="water", timeout=30, interval=1) is None:
        logging.info("Did not find the keyword 'water' in the menu. Did Keras navigate to the advanced menu correctly?")
        sys.exit(1)

    am.take_screenshot("advanced_1.png", ArtifactType.CONFIG_IMAGE, "first screenshot of advanced settings menu")
    time.sleep(0.5)

    result = keras_service.look_for_word("water", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the keyword 'water' in the menu. Did Keras navigate to the advanced menu correctly?")
        sys.exit(1)
    gui.moveTo(result["x"], result["y"])
    time.sleep(1)

    # Scroll to the middle of the advanced menu
    mouse_scroll_n_times(15, -1, 0.1)
    if keras_service.wait_for_word(word="heat", timeout=30, interval=1) is None:
        logging.info("Did not find the keyword 'heat' in the menu. Did Keras scroll down the advanced menu far enough?")
        sys.exit(1)
    am.take_screenshot("advanced_2.png", ArtifactType.CONFIG_IMAGE, "second screenshot of advanced settings menu")
    time.sleep(0.5)

    # Scroll to the bottom of the advanced menu
    mouse_scroll_n_times(15, -1, 0.1)
    if keras_service.wait_for_word(word="bodies", timeout=30, interval=1) is None:
        logging.info("Did not find the keyword 'bodies' in the menu. Did Keras scroll down the advanced menu far enough?")
        sys.exit(1)
    am.take_screenshot("advanced_3.png", ArtifactType.CONFIG_IMAGE, "third screenshot of advanced settings menu")
    time.sleep(0.5)

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

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = keras_service.wait_for_word("fps", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time()) - 2

    time.sleep(90)  # Wait time for battle benchmark

    result = keras_service.wait_for_word("summary", interval=0.2, timeout=250)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    # Wait 5 seconds for benchmark info
    test_end_time = int(time.time()) - 1
    time.sleep(5)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    time.sleep(0.5)
    am.copy_file(Path(cfg), ArtifactType.CONFIG_TEXT, "preferences.script.txt")

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    am.create_manifest()

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
    keras_service = OcrService(args.keras_host, args.keras_port)
    start_time, endtime = run_benchmark(keras_service)
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID)
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
