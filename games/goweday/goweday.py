"""Gears of War E-Day test script"""

import logging
import os
import re
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.file_cleanup import remove_files
from harness_utils.input import hold, mangohud_log_toggle, move_mouse, press
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import game_install_path, harness_directories, local_appdata
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import exec_steam_game, get_build_id

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 3010850
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "GoWEDay-Steam.exe"
VIDEO_PATH = game_install_path(STEAM_GAME_ID) / "FairlightConcept" / "Content" / "Movies"

CONFIG_PATH = (
    local_appdata(STEAM_GAME_ID)
    / "Microsoft"
    / "Gears of War E-Day"
    / "Steam"
    / "6BE41AB5"
    / "Saved"
    / "Config"
    / "Windows"
)
CONFIG_FILENAME = "GameUserSettings.ini"
CONFIG = CONFIG_PATH / CONFIG_FILENAME

intro_video = VIDEO_PATH / "Bootflow_Logos.bk2"


def get_resolution():
    """Get current resolution from settings file"""
    if not CONFIG.exists():
        raise RuntimeError(f"Missing path: {CONFIG}")
    logger.info("Reading Gears of War: E-Day settings file path=%s", CONFIG)
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    height = None
    width = None
    with open(CONFIG, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = int(height_match.group(1))
            if width_match is not None:
                width = int(width_match.group(1))
            if height is not None and width is not None:
                return (width, height)
    return (width, height)


def navigate_to_settings():
    """navigate from main menu to settings menu"""
    logger.info("Navigating main menu")
    hold("x",4)
    result = find_word("campaign", timeout=10)
    if not result:
        logger.info(
            "Did not see the main menu. Did OCR navigate to the settings menu correctly?"
        )
        sys.exit(1)
    move_mouse(0, 0)
    press("2, enter")
    result = find_word("controls", timeout=10)
    if not result:
        logger.info(
            "Did not see the control options. Did OCR navigate to the settings menu correctly?"
        )
        sys.exit(1)
    press("e")


def navigate_settings() -> None:
    """Simulate inputs to navigate the main menu"""
    navigate_to_settings()
    result = find_word("hdr", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the hdr options. Did OCR navigate to the settings menu correctly?"
        )
        sys.exit(1)
    # entered settings
    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_1.png")
    press("down*13")

    result = find_word("preset", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the preset option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_2.png")

    press("down*8")

    result = find_word("geometry", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the ray tracing geometry option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_3.png")

    press("down*10")

    result = find_word("grain", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see film grain option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_4.png")

    press("down*6")

    result = find_word("gore", interval=3, timeout=20)
    if not result:
        logger.info(
            "Did not see the gore quality option. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_5.png")

    press("4")


def run_benchmark():
    """Start the benchmark"""
    remove_files([str(intro_video)])

    # Start game via Steam and enter fullscreen mode
    setup_start_time = int(time.time())
    exec_steam_game(STEAM_GAME_ID)

    time.sleep(30)

    result = find_word("start", interval=3, timeout=60)
    if not result:
        logger.info("Did not see start screen. Did the game launch?")
        sys.exit(1)

    if is_linux():
        mangohud_log_toggle()

    navigate_settings()

    # Start the benchmark!
    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logger.info("Harness setup took %f seconds", elapsed_setup_time)

    result = find_word("restart", timeout=90, interval=0.2)
    if not result:
        logger.info("Benchmark didn't start.")
        sys.exit(1)

    test_start_time = int(time.time())

    logger.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(58)
    result = find_word("summary", timeout=240, interval=0.5)
    if not result:
        logger.info("Did not see benchmark summary screen. Check settings or mark as DNF.")
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
