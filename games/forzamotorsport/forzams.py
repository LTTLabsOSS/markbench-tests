"""Forza Motorsport test script"""

import logging
import os
import sys
import time
from pathlib import Path

import pydirectinput as user
from forzams_utils import get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.files import copy_to_directory, reset_directory
from harness_utils.screenshot import capture_screenshot_png
from harness_utils.input import press_n_times
from harness_utils.ocr_service import find_word
from harness_utils.report import seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command, get_build_id

STEAM_GAME_ID = 2440510
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
ARTIFACTS_DIRECTORY = LOG_DIRECTORY / "artifacts"
LOCAL_USER_SETTINGS = (
    Path(os.getenv("LOCALAPPDATA"))
    / "Microsoft.ForzaMotorsport"
    / "User_SteamLocalStorageDirectory"
    / "ConnectedStorage"
    / "ForzaUserConfigSelections"
    / "UserConfigSelections"
)
PROCESSES = ["forza_steamworks_release_final.exe", "RTSS.exe"]

user.FAILSAFE = False


def start_rtss():
    """Sets up the RTSS process"""
    profile_path = SCRIPT_DIRECTORY / "forza_steamworks_release_final.exe.cfg"
    copy_rtss_profile(str(profile_path))
    return start_rtss_process()


def run_benchmark() -> tuple[int, int]:
    """Run the benchmark"""
    start_rtss()
    # Give RTSS time to start
    time.sleep(10)
    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    reset_directory(ARTIFACTS_DIRECTORY)

    time.sleep(50)

    # Make sure the game started correctly
    if find_word(word="play", timeout=30, interval=1) is None:
        logging.info("Could not find the main menu. Did the game load?")
        sys.exit(1)

    # Navigate to display menu
    user.press("f")
    time.sleep(1)

    if find_word(word="contrast", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the accessibility settings menu. Did the menu get stuck?"
        )
        sys.exit(1)

    user.press("]")
    time.sleep(0.5)
    user.press("]")
    time.sleep(0.5)
    user.press("]")
    time.sleep(0.5)

    # Verify that we have navigated to the video settings menu and take a screenshot
    if find_word(word="resolution", timeout=30, interval=1) is None:
        logging.info("Did not find the display settings menu. Did the menu get stuck?")
        sys.exit(1)

    capture_screenshot_png(ARTIFACTS_DIRECTORY / "display.png")
    user.press("]")
    time.sleep(0.5)

    if find_word(word="filtering", timeout=30, interval=1) is None:
        logging.info("Did not find the graphics settings menu. Did the menu get stuck?")
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "graphics1.png")

    press_n_times("down", 15, 0.5)

    if find_word(word="particle", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the particle effect settings. Did the menu get stuck?"
        )
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "graphics2.png")

    press_n_times("down", 3, 0.5)
    user.press("up")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)

    if find_word(word="flare", timeout=30, interval=1) is None:
        logging.info("Did not find the lens flare settings. Did the menu get stuck?")
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "graphics3.png")

    # Navigate to graphics menu
    user.press("[")
    time.sleep(0.5)
    user.press("enter")

    setup_end_time = int(time.time())
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logging.info("Setup took %s seconds", elapsed_setup_time)

    time.sleep(15)

    if find_word(word="results", timeout=60, interval=0.5) is None:
        logging.info("Did not find the results screen. Did the game load?")
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "results.png")

    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(180)

    # Wait for results screen to display info
    if find_word(word="results", timeout=15, interval=0.5) is None:
        logging.info(
            "Did not find the results screen. Did the game crash during the run?"
        )
        sys.exit(1)

    test_end_time = round(int(time.time()))
    # Give results screen time to fill out, then save screenshot and config file
    time.sleep(2)
    copy_to_directory(LOCAL_USER_SETTINGS, ARTIFACTS_DIRECTORY)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %s seconds", elapsed_test_time)

    for proc_name in PROCESSES:
        terminate_process(proc_name)


    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    resolution = get_resolution(str(LOCAL_USER_SETTINGS))
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for process_name in PROCESSES:
        terminate_process(process_name)
    sys.exit(1)
