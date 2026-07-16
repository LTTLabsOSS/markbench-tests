"""Strange Brigade test script"""

import logging
import os
import sys
import time
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from strangebrigade_utils import read_current_resolution, replace_exe, restore_exe

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.input import press_n_times
from harness_utils.ocr_service import find_word
from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact
from harness_utils.paths import harness_directories
from harness_utils.file_cleanup import remove_files
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import (
    exec_steam_run_command,
    get_app_install_location,
    get_build_id,
)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "StrangeBrigade.exe"
STEAM_GAME_ID = 312670
CAPTURE_PATH = SCRIPT_DIRECTORY / "capture"
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{LOCALAPPDATA}\\Strange Brigade"
CONFIG_FILENAME = "GraphicsOptions.ini"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
EXE_PATH = get_app_install_location(STEAM_GAME_ID) / "bin"
VIDEO_PATH = get_app_install_location(STEAM_GAME_ID) / "FMV"

user.FAILSAFE = False

intro_videos = [VIDEO_PATH / "rebellion.webm"]


def run_benchmark():
    """Starts the benchmark"""
    logging.info(intro_videos)
    remove_files([str(path) for path in intro_videos])
    replace_exe()
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    time.sleep(30)

    result = find_word("options", timeout=30, vulkan=True)
    if not result:
        logging.info("Did not find the options menu. Did the game launch?")
        sys.exit(1)

    press_n_times("down", 5, 0.2)
    user.press("left")
    time.sleep(0.2)
    user.press("enter")

    result = find_word("display", timeout=10, vulkan=True)
    if not result:
        logging.info("Did not find the display menu. Did OCR navigate correctly?")
        sys.exit(1)

    gui.press("pgdn")

    result = find_word("customise", timeout=10, vulkan=True)
    if not result:
        logging.info(
            "Did not find the customize graphics detail option. Did navigate correctly?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display.png", vulkan=True)

    time.sleep(0.5)
    user.press("escape")

    press_n_times("down", 5, 0.2)
    user.press("enter")

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    time.sleep(1)
    result = find_word("strange", timeout=100, vulkan=True)
    if not result:
        logging.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())

    time.sleep(55)  # Wait time for battle benchmark

    result = find_word("confirm", interval=0.2, timeout=250, vulkan=True)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    test_end_time = int(time.time()) - 1

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png", vulkan=True)
    copy_artifact(Path(CONFIG_FULL_PATH), ARTIFACTS_DIRECTORY)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_process(PROCESS_NAME)

    time.sleep(5)
    restore_exe()

    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

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
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
