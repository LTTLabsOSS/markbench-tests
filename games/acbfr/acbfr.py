"""Assassins Creed Black Flag Resynced test script"""

import logging
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from acbfr_utils import get_resolution

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.file_cleanup import remove_files
from harness_utils.input import mangohud_log_toggle, press, user
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, game_install_path, user_documents
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.report import format_resolution, seconds_to_milliseconds, write_report_json
from harness_utils.steam import exec_steam_game, get_build_id

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 3751950
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "ACBlackFlag.exe"
VIDEO_PATH = game_install_path(STEAM_GAME_ID) / "videos"

CONFIG_PATH = user_documents(STEAM_GAME_ID) / "Assassin's Creed Black Flag Resynced"
CONFIG_FILENAME = "ACBlackFlag.ini"
CONFIG = CONFIG_PATH / CONFIG_FILENAME

intro_videos = [
    VIDEO_PATH / "ANVIL_Logo.webm",
    VIDEO_PATH / "HUB_Bootflow_AbstergoIntro.webm",
    VIDEO_PATH / "HUB_Bootflow_FranchiseIntro.webm",
    VIDEO_PATH / "HUB_Bootflow_Intro.webm",
    VIDEO_PATH / "HUB_Bootflow_Intro_LowRes.webm",
    VIDEO_PATH / "UbisoftLogo.webm",
    VIDEO_PATH / "en" / "Epilepsy.webm",
    VIDEO_PATH / "en" / "warning_disclaimer.webm",
    VIDEO_PATH / "en" / "WarningSaving.webm",
    ]
user.FAILSAFE = False

def navigate_to_settings():
    """navigate from main menu to settings menu"""
    logger.info("Navigating main menu")
    press("enter")
    result = find_word("system", timeout=10)
    if not result:
        logger.info(
            "Did not see the main menu. Did OCR navigate to the settings menu correctly?"
        )
        sys.exit(1)
    press("down, enter")
    result = find_word("options", timeout=10)
    if not result:
        logger.info(
            "Did not see the system options. Did OCR navigate to the settings menu correctly?"
        )
        sys.exit(1)
    press("enter")


def navigate_settings() -> None:
    """Simulate inputs to navigate the main menu"""
    navigate_to_settings()
    result = find_word("display", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the display options. Did OCR navigate to the settings menu correctly?"
        )
        sys.exit(1)
    # entered settings
    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display_1.png")
    press("down*13")

    result = find_word("maximum", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the maximum dynamic resolution option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display_2.png")

    press("down*7")

    result = find_word("aberration", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the chromatic aberration option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display_3.png")

    press("c")
    time.sleep(1)

    result = find_word("raytracing", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see raytracing mode option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_1.png")

    press("down*10")

    result = find_word("loading", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the loading distance option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_2.png")

    press("down*6")

    result = find_word("cloud", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the cloud quality option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_3.png")

    press("down*5")
    
    result = find_word("texture", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see terrain texture quality option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_4.png")

    press("f2")


def run_benchmark():
    """Start the benchmark"""
    remove_files([str(path) for path in intro_videos])

    # Start game via Steam and enter fullscreen mode
    setup_start_time = int(time.time())
    exec_steam_game(STEAM_GAME_ID)

    time.sleep(100)

    result = find_word("unsupported", interval=3, timeout=30)
    if result:
        press("enter")

    result = find_word("edward", interval=3, timeout=60)
    if not result:
        logger.info("Did not see Edward's name. Did the game launch?")
        sys.exit(1)

    if is_linux():
        mangohud_log_toggle()

    navigate_settings()

    # Start the benchmark!
    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logger.info("Harness setup took %f seconds", elapsed_setup_time)

    result = find_word("leave", timeout=60, interval=0.2)
    if not result:
        logger.info("Benchmark didn't start.")
        sys.exit(1)

    test_start_time = int(time.time()) + 4

    logger.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(138)
    result = find_word("results", timeout=240, interval=0.5)
    if not result:
        logger.info("Did not see results screen. Mark as DNF.")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")

    test_end_time = int(time.time())
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)
    copy_artifact(CONFIG, ARTIFACTS_DIRECTORY)
    if is_linux():
        mangohud_log_toggle()
    terminate_process(PROCESS_NAME)
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
except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    terminate_process(PROCESS_NAME)
    sys.exit(1)
