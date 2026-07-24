"""Total War: Warhammer III test script"""

import logging
import os
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from twwh3_utils import read_current_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact, create_artifacts_manifest
from harness_utils.paths import harness_directories
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import get_app_install_location, get_build_id

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "Warhammer3.exe"
STEAM_GAME_ID = 1142710

APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Warhammer3\\scripts"
CONFIG_FILENAME = "preferences.script.txt"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"

user.FAILSAFE = False


def start_game():
    """Starts the game process"""
    cmd_string = f'start /D "{get_app_install_location(STEAM_GAME_ID)}" {PROCESS_NAME}'
    logger.info(cmd_string)
    return os.system(cmd_string)


def skip_logo_screens() -> None:
    """Simulate input to skip logo screens"""
    logger.info("Skipping logo screens")

    # Enter menu
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)


def run_benchmark():
    """Starts the benchmark"""
    start_game()
    setup_start_time = int(time.time())
    time.sleep(5)

    result = find_word("warning", timeout=50, interval=5)
    if not result:
        logger.info("Did not see warnings. Did the game start?")
        sys.exit(1)

    skip_logo_screens()
    time.sleep(2)

    result = find_word("options", timeout=10, interval=1)
    if not result:
        logger.info("Did not find the options menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "main.png")

    result = find_word("ad", timeout=10, interval=1)
    if not result:
        logger.info("Did not find the advanced menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.5)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "advanced.png")

    result = find_word("bench", timeout=10, interval=1)
    if not result:
        logger.info("Did not find the benchmark menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    if args.benchmark != "battle":
        result = find_word("mirrors", timeout=10, interval=1)
        gui.moveTo(result["x"], result["y"])
        time.sleep(0.2)
        gui.mouseDown()
        time.sleep(0.2)
        time.sleep(2)
        user.press("enter")
    else:
        time.sleep(2)
        user.press("enter")

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)

    result = find_word("fps", interval=0.5, timeout=100)
    if not result:
        logger.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())

    if args.benchmark != "battle":
        time.sleep(65)  # Wait time for MOM benchmark
    else:
        time.sleep(100)  # Wait time for battle benchmark

    result = find_word("summary", interval=0.2, timeout=250)
    if not result:
        logger.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    test_end_time = int(time.time()) - 1

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    copy_artifact(Path(CONFIG_FULL_PATH), ARTIFACTS_DIRECTORY)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_process(PROCESS_NAME)


    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

parser = ArgumentParser()
parser.add_argument(
    "-s",
    "--benchmark",
    dest="benchmark",
    help="Benchmark Scene",
    metavar="benchmark",
    required=True,
)
args, unknown = parser.parse_known_args()

try:
    start_time, endtime = run_benchmark()
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
except Exception as e:
    logger.error("Something went wrong running the benchmark!")
    logger.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
