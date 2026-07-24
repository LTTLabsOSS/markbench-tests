"""Rainbow Six Siege test script"""

import logging
from pathlib import Path
import time
import sys
import vgamepad as vg
from r6siege_utils import (
    read_current_resolution,
    get_r6s_config_path,
    find_latest_result_file,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.process import terminate_process
from harness_utils.input import user
from harness_utils.output_logging import setup_logging
from harness_utils.ocr_service import find_word
from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact, create_artifacts_manifest
from harness_utils.paths import harness_directories
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import exec_steam_game, get_build_id
from harness_utils.controllers import LTTGamePadDS4

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "rainbowsix.exe"
STEAM_GAME_ID = 359550
GAMEPAD = LTTGamePadDS4()


def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID)


def run_benchmark():
    """Starts the benchmark"""
    setup_start_time = int(time.time())
    start_game()
    time.sleep(90)

    # Checking for the main menu
    if find_word(word="conflict", interval=1, timeout=15):
        user.press("down")
        time.sleep(0.4)
        user.press("enter")
        time.sleep(30)

    # Checking for the main menu
    if find_word(word="shop", interval=1, timeout=60) is None:
        logger.info("Did not find the main menu. Did the game load?")
        sys.exit(1)

    # Navigating to the options
    GAMEPAD.press(button=vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS)

    if find_word(word="options", interval=0.5, timeout=100) is None:
        logger.info(
            "Could not find the options menu. Was something else on the screen?"
        )
        sys.exit(1)

    GAMEPAD.press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    # Navigating to the display settings and screenshotting
    if find_word(word="general", interval=0.5, timeout=100) is None:
        logger.info(
            "Could not find the general options. Did it navigate to the settings correctly?"
        )
        sys.exit(1)

    GAMEPAD.press_n_times(
        button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT, n=3, pause=0.3
    )

    if find_word(word="monitor", interval=0.5, timeout=100) is None:
        logger.info(
            "Could not find the monitor. Did it navigate to the display settings correctly?"
        )
        sys.exit(1)

    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display1.png")
    time.sleep(1)
    GAMEPAD.dpad_press_n_times(
        direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=12, pause=0.3
    )
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display2.png")
    time.sleep(1)

    # Navigating to the graphics settings and screenshotting
    GAMEPAD.press(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)

    if find_word(word="filtering", interval=0.5, timeout=100) is None:
        logger.info(
            "Could not find the texture filtering setting. Did it navigate to the graphics settings correctly?"
        )
        sys.exit(1)

    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics1.png")
    time.sleep(1)

    GAMEPAD.dpad_press_n_times(
        direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=17, pause=0.3
    )

    if find_word(word="fps", interval=0.5, timeout=100) is None:
        logger.info(
            "Could not find the TAA sharpness setting. Did it navigate the graphics settings correctly?"
        )
        sys.exit(1)

    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics2.png")
    time.sleep(1)

    GAMEPAD.dpad_press_n_times(
        direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=3, pause=0.3
    )

    if find_word(word="sharpness", interval=0.5, timeout=100) is None:
        logger.info(
            "Could not find the TAA sharpness setting. Did it navigate the graphics settings correctly?"
        )
        sys.exit(1)

    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics3.png")
    time.sleep(1)

    # Starting the benchmark
    GAMEPAD.press(button=vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT)

    elapsed_setup_time = int(time.time() - setup_start_time)
    logger.info("Setup took %f seconds", elapsed_setup_time)

    if find_word(word="skip", interval=0.5, timeout=100) is None:
        logger.info("Could not find the skip dialog. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())
    time.sleep(76)

    if find_word(word="results", interval=0.2, timeout=250) is None:
        logger.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    test_end_time = int(time.time() - 1)
    time.sleep(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    copy_artifact(find_latest_result_file(), ARTIFACTS_DIRECTORY)

    # Wait 5 seconds for benchmark info
    time.sleep(2)

    # End the run
    elapsed_test_time = int(test_end_time - test_start_time)
    logger.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    config_path = get_r6s_config_path()
    if config_path is None:
        logger.warning("GameSettings.ini was not found")
        sys.exit(1)
    copy_artifact(config_path, ARTIFACTS_DIRECTORY)
    terminate_process(PROCESS_NAME)

    resolution = read_current_resolution()
    if resolution is None:
        logger.warning("Current resolution was not found in GameSettings.ini")
        sys.exit(1)
    width, height = resolution
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    logger.info("Waiting for Siege X to fully exit now.")
    time.sleep(30)  # sleeping to let the game processes finish closing

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)


def main():
    """entry point"""
    setup_logging(LOG_DIRECTORY)
    run_benchmark()


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logger.error("Something went wrong running the benchmark!")
        logger.exception(ex)
        terminate_process(PROCESS_NAME)
        sys.exit(1)
