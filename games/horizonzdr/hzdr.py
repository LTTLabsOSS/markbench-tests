"""Horizon Zero Dawn Remastered test script"""

import logging
import sys
import time
import winreg
from pathlib import Path

import pydirectinput as user
from hzdr_utils import get_resolution, process_registry_file

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.ocr_service import find_word
from harness_utils.artifacts import copy_artifact, reset_artifacts, save_screenshot
from harness_utils.paths import harness_directories
from harness_utils.files import remove_files
from harness_utils.report import format_resolution, seconds_to_milliseconds
from harness_utils.output_logging import setup_logging
from harness_utils.report_writing import write_report_json
from harness_utils.process import terminate_process
from harness_utils.steam import (
    exec_steam_run_command,
    get_build_id,
    get_steamapps_common_path,
)

STEAM_GAME_ID = 2561580
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "HorizonZeroDawnRemastered.exe"
VIDEO_PATH = (
    get_steamapps_common_path() / "Horizon Zero Dawn Remastered" / "Movies" / "Mono"
)
INPUT_FILE = SCRIPT_DIRECTORY / "graphics.reg"
CONFIG_FILE = SCRIPT_DIRECTORY / "graphics_config.txt"
hive = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\\Guerrilla Games\\Horizon Zero Dawn Remastered\\Graphics"

user.FAILSAFE = False

intro_videos = [
    VIDEO_PATH / "weaseltron_logo.bk2",
    VIDEO_PATH / "sony_studios_reel.bk2",
    VIDEO_PATH / "nixxes_logo.bk2",
    VIDEO_PATH / "Logo.bk2",
    VIDEO_PATH / "guerilla_logo.bk2",
]


def run_benchmark() -> tuple[float]:
    """Run the benchmark"""
    logging.info("Removing intro videos")
    remove_files([str(path) for path in intro_videos])

    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    reset_artifacts(ARTIFACTS_DIRECTORY)

    time.sleep(10)
    # skip intro
    user.press("esc")
    # Make sure the game started correctly
    if find_word(word="quit", timeout=30, interval=1) is None:
        logging.info("Could not find the main menu. Did the game load?")
        sys.exit(1)

    # Navigate to options menu
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(0.5)

    if find_word(word="language", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    user.press("e")
    time.sleep(0.5)

    # Verify that we have navigated to the display settings menu and take a screenshot
    if find_word(word="monitor", timeout=30, interval=1) is None:
        logging.info("Did not find the display settings menu. Did the menu get stuck?")
        sys.exit(1)
    # Check if its fullscreen only and not exclusive fullscreen
    if find_word(word="exclusive", timeout=3) is None:
        user.press("down")
        user.press("right")
        # Resets focus to first position before applying settings
        user.press("up")
        user.press("r")
        user.press("enter")
        time.sleep(1)
        user.press("enter")
    # Checks frame rate setting, sometimes this can be incorrect even if it is set to exclusive fullscreen
    if find_word(word="144", timeout=3) is None:
        user.press("down")
        # Sometimes when the screen refreshes if the setting is changed from fullscreen to exclusive, the cursor highlights on v-sync because technically it moves it to the center so the game picks that up as a focusing movement.
        # This checks if we are in the proper position by going down one and seeing if we can see 'generation' from frame generation, which should not be visible if we are in the correct focus location
        # Either position once known is routed to the correct position via this if/else statement
        if find_word(word="generation", timeout=3):
            user.press("up")
            user.press("up")
        else:
            user.press("down")
            user.press("down")
            user.press("down")
            user.press("down")
            user.press("down")
            user.press("right")
        # This while loop is for the case when we switch to exclusive fullscreen from fullscreen, occasionally it will set to 30Hz, we want to get to 144Hz
        # So we should be highlighted on refresh rate at this point, it will (if not 144) do the first user.input("right") then check for 144, if not present it will continue pressing right and checking after for 144
        # This solves arbitrary steps to get to 144Hz, and sets us up if we want to alter that target hz setting we can just change the word variable below.
        # KNOWN LIMITATION  we can maybe pull the max refresh some other way if we care about whether the display is not 144Hz max, so as to handle all edge cases here.
        while find_word(word="144", timeout=1) is None:
            user.press("right")
        # Apply Hz setting once it is correct, then go up one so the proper settings are in view for the screenshot
        user.press("r")
        user.press("enter")
        time.sleep(1)
        user.press("enter")
        user.press("up")
        user.press("up")
        user.press("up")
        user.press("up")
        user.press("up")
        user.press("up")
    save_screenshot(ARTIFACTS_DIRECTORY / "display1.png")

    user.press("up")
    time.sleep(0.5)

    if find_word(word="upscale", timeout=30, interval=1) is None:
        logging.info("Did not find the upscale settings. Did the menu not scroll?")
        sys.exit(1)
    save_screenshot(ARTIFACTS_DIRECTORY / "display2.png")

    # Navigate to graphics menu
    user.press("e")
    time.sleep(0.5)

    if find_word(word="preset", timeout=30, interval=1) is None:
        logging.info("Did not find the graphics settings menu. Did the menu get stuck?")
        sys.exit(1)
    save_screenshot(ARTIFACTS_DIRECTORY / "graphics1.png")

    user.press("up")
    time.sleep(0.5)

    if find_word(word="sharpness", timeout=30, interval=1) is None:
        logging.info("Did not find the sharpness settings. Did the menu not scroll?")
        sys.exit(1)
    save_screenshot(ARTIFACTS_DIRECTORY / "graphics2.png")

    # Launch the benchmark
    user.press("tab")
    time.sleep(0.5)
    user.press("enter")

    setup_end_time = int(time.time())
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logging.info("Setup took %s seconds", elapsed_setup_time)

    if find_word(word="continue", timeout=120, interval=1) is None:
        logging.info(
            "Did not find the continue button. Did the game not finish loading?"
        )
        sys.exit(1)

    user.press("enter")

    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(180)

    # Wait for results screen to display info
    if find_word(word="results", timeout=20, interval=0.1) is None:
        logging.info(
            "Did not find the results screen. Did the game not finish the benchmark?"
        )
        sys.exit(1)

    test_end_time = round(int(time.time()))
    # Give results screen time to fill out, then save screenshot and config file
    time.sleep(2)
    save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    process_registry_file(hive, SUBKEY, str(INPUT_FILE), str(CONFIG_FILE))
    copy_artifact(CONFIG_FILE, ARTIFACTS_DIRECTORY)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %s seconds", elapsed_test_time)

    terminate_process(PROCESS_NAME)

    time.sleep(15)
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution(str(CONFIG_FILE))
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
