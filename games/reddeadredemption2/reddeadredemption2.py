"""Red Dead Redemption 2 test script"""

import getpass
import logging
import sys
import time
from pathlib import Path

import pydirectinput as user
from red_dead_redemption_2_utils import get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact, create_artifacts_manifest
from harness_utils.paths import harness_directories
from harness_utils.input import press_n_times
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_run_command, get_build_id

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 1174180
PROCESS_NAME = "RDR2.exe"
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
CONFIG_FULL_PATH = Path(
    "C:/Users/",
    getpass.getuser(),
    "Documents",
    "Rockstar Games",
    "Red Dead Redemption 2",
    "Settings",
    "system.xml",
)

user.FAILSAFE = False


def run_benchmark():
    """Starts the benchmark"""
    # Wait for game to load to main menu
    setup_start_time = int(time.time())
    exec_steam_run_command(STEAM_GAME_ID)

    time.sleep(80)

    # patch to look for seasonal popup
    result = find_word("strange", vulkan=True, timeout=30)
    if result:
        user.press("enter")
        time.sleep(3)

    # Press Z to enter settings
    result = find_word("settings", vulkan=True, timeout=30)
    if not result:
        logger.info("Did not find the settings menu. Did the game launch?")
        sys.exit(1)
    user.press("z")
    time.sleep(3)

    # Enter graphics menu
    ## ensure we are starting from the top left of the screen
    result = find_word("graphics", vulkan=True, timeout=5)
    if not result:
        logger.info("Did not find the graphics menu. Did OCR get stuck?")
        sys.exit(1)
    user.press("up")
    user.press("up")
    user.press("left")
    user.press("left")
    user.press("down")
    user.press("enter")
    time.sleep(3)

    # Take pictures of the graphics settings
    result = find_word("resolution", vulkan=True, timeout=5)
    if not result:
        logger.info(
            "Did not find the resolution setting. Did the game navigate correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics1.png", vulkan=True)

    result = find_word("nvidia", vulkan=True, timeout=5)
    if result:
        logger.info("NVIDIA card is installed, navigating accordingly.")
        press_n_times("down", 26, 0.2)

        result = find_word("mode", vulkan=True, timeout=5)
        if not result:
            logger.info(
                "Did not find the FSR mode description. Did it navigate correctly?"
            )
            sys.exit(1)
        capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics2.png", vulkan=True)
        press_n_times("down", 14, 0.2)

        result = find_word("long", vulkan=True, timeout=5)
        if not result:
            logger.info(
                "Did not find the Long Shadows settings. Did it navigate correctly?"
            )
            sys.exit(1)
        capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics3.png", vulkan=True)
        press_n_times("down", 15, 0.2)

        result = find_word("tessellation", vulkan=True, timeout=5)
        if not result:
            logger.info(
                "Did not find the Tree Tessellation settings. Did OCR navigate correctly?"
            )
            sys.exit(1)
        capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics4.png", vulkan=True)

    else:
        logger.info("NVIDIA card not detected on screen, navigating accordingly.")
        press_n_times("down", 26, 0.2)

        result = find_word("msaa", vulkan=True, timeout=5)
        if not result:
            logger.info("Did not find the MSAA settings. Did OCR navigate correctly?")
            sys.exit(1)
        capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics2.png", vulkan=True)
        press_n_times("down", 14, 0.2)

        result = find_word("reflection", vulkan=True, timeout=5)
        if not result:
            logger.info(
                "Did not find the Water Reflection Quality settings. Did OCR navigate correctly?"
            )
            sys.exit(1)
        capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics3.png", vulkan=True)
        press_n_times("down", 12, 0.2)

        result = find_word("tessellation", vulkan=True, timeout=5)
        if not result:
            logger.info(
                "Did not find the Tree Tessellation settings. Did OCR navigate correctly?"
            )
            sys.exit(1)
        capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Graphics4.png", vulkan=True)

    # Run benchmark by holding X for 2 seconds
    result = find_word("benchmark", vulkan=True, timeout=5)
    if not result:
        logger.info(
            "Did not see the Run Benchmark Test at the bottom of the screen. Did navigation mess up?"
        )
        sys.exit(1)
    user.keyDown("x")
    time.sleep(1.5)
    user.keyUp("x")

    # Press enter to confirm benchmark
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)
    user.press("enter")

    # Looking for the word Stop to mark the in time
    result = find_word("stop", vulkan=True, timeout=60, interval=1)
    if not result:
        logger.info(
            "Did not find the stop benchmarking in the corner. Did the benchmark crash?"
        )
        sys.exit(1)
    test_start_time = int(time.time())

    # Wait for the benchmark to complete
    time.sleep(270)  # 4 min, 30 seconds.
    result = find_word("end", vulkan=True, timeout=30, interval=1)
    if not result:
        logger.info("Did not find the end results screen. Did the benchmark crash?")
        sys.exit(1)
    test_end_time = int(time.time())
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png", vulkan=True)
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)
    copy_artifact(Path(CONFIG_FULL_PATH), ARTIFACTS_DIRECTORY)

    # Exit
    terminate_process(PROCESS_NAME)

    time.sleep(50)  # sleeping to let the rockstar processes finish closing
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)


try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
except Exception as e:
    logger.error("Something went wrong running the benchmark!")
    logger.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
