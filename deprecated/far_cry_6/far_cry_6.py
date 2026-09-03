"""Far Cry 6 test script"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from far_cry_6_utils import get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.input import press, scroll, user
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.process import terminate_process
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "FarCry6.exe"
GAME_ID = 5266
username = os.getlogin()
XML_FILE = rf"C:\Users\{username}\Documents\My Games\Far Cry 6\gamerprofile.xml"


def start_game():
    subprocess.run(f"start uplay://launch/{GAME_ID}/0", shell=True, check=True)


def skip_logo_screens() -> None:
    """Simulate input to skip logo screens"""
    logger.info("Skipping logo screens")

    # skipping the logo screens
    press("space*10")


def run_benchmark():
    start_game()
    setup_start_time = int(time.time())
    time.sleep(25)

    # skipping game intros
    result = find_word("government", timeout=20, interval=1)
    if not result:
        logger.info("Did not see 'government'. Did the game start?")
        sys.exit(1)

    skip_logo_screens()

    result = find_word("original", timeout=20, interval=1)
    if not result:
        logger.info("Did not see the Far Cry 6 intro video. Did the game crash?")
        sys.exit(1)

    press("space*2")

    time.sleep(2)

    # navigating the menus to get to the video settings
    result = find_word("later", timeout=5, interval=1)
    if result:
        press("escape")

    result = find_word("options", timeout=10, interval=1)
    if not result:
        logger.info("Did not find the main menu. Did the game skip the intros?")
        sys.exit(1)

    user.click(result["x"], result["y"])
    time.sleep(0.2)
    time.sleep(2)

    result = find_word("video", timeout=10, interval=1)
    if not result:
        logger.info("Did not find the options menu. Did OCR click incorrectly?")
        sys.exit(1)

    user.click(result["x"], result["y"])
    time.sleep(0.2)
    time.sleep(2)

    # grabbing screenshots of all the video settings
    result = find_word("adapter", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the Video Adapter setting in the monitor options. Did OCR navigate wrong?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video.png")

    time.sleep(2)

    press("e")

    result = find_word("filtering", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the Texture Filtering setting in the quality options. Did OCR navigate wrong?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "quality1.png")

    time.sleep(2)

    scroll(-800, 8)

    result = find_word("shading", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the FidelityFX Variable Shading setting in the quality options. Did OCR navigate wrong?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "quality2.png")

    time.sleep(2)

    press("e*2")

    result = find_word("lock", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the Enable Framerate Lock setting in the advanced options. Did OCR navigate wrong?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "advanced.png")

    # starting the benchmark
    time.sleep(2)
    press("f5")
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)

    result = find_word("toggle", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the toggle ui button in the lower right. Did the benchmark crash?"
        )
        sys.exit(1)
    test_start_time = int(time.time())

    time.sleep(60)  # wait for benchmark to complete

    result = find_word("results", interval=0.5, timeout=100)
    if not result:
        logger.info("Didn't find the results screen. Did the benchmark crash?")
        sys.exit(1)

    test_end_time = int(time.time()) - 1

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    time.sleep(1)

    # Exit
    terminate_process(PROCESS_NAME)
    copy_artifact(XML_FILE, ARTIFACTS_DIRECTORY)

    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)


try:
    test_start_time, test_end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": "unknown",
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    terminate_process(PROCESS_NAME)
    sys.exit(1)
