"""Cities: Skylines II"""

import logging
import sys
import time
from pathlib import Path

from cities_skylines_2_utils import (
    CONFIG_FULL_PATH,
    copy_benchmarksave,
    copy_continuegame,
    copy_launcherfiles,
    copy_launcherpath,
    read_current_resolution,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.input import click, move_mouse, press, scroll
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.process import terminate_process
from harness_utils.report import seconds_to_milliseconds, write_report_json
from harness_utils.steam import exec_steam_game, get_build_id

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "cities2.exe"
STEAM_GAME_ID = 949230
launcher_files = ["bootstrapper-v2.exe", "launcher.exe", "notlauncher-options.json"]
save_files = ["Benchmark.cok", "Benchmark.cok.cid"]
config_files = ["UserState.coc"]


def run_benchmark():
    """Run the benchmark."""
    copy_launcherfiles(launcher_files)
    copy_launcherpath()
    copy_benchmarksave(save_files)
    copy_continuegame(config_files)

    exec_steam_game(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    time.sleep(14)

    if not find_word("paradox", interval=0.5, timeout=100):
        logger.info("Could not find the Paradox logo. Did the game launch?")
        sys.exit(1)
    press("escape*3")

    if not find_word("new", interval=0.5, timeout=100):
        logger.info("Did not find the main menu. Did the game crash?")
        sys.exit(1)

    result = find_word("load", timeout=10, interval=1)
    if not result:
        logger.info("Did not find the load game option. Did the save game copy?")
        sys.exit(1)

    # Navigate to load save menu
    click(result["x"], result["y"])

    result = find_word("benchmark", timeout=10, interval=1, crop="top_left")
    if not result:
        logger.info(
            "Did not find the save game original date. Did the OCR click correctly?"
        )
        sys.exit(1)

    # Loading the game
    click(result["x"], result["y"])
    press("enter")

    if not find_word("grand", interval=0.5, timeout=100):
        logger.info(
            "Could not find the paused notification. Unable to mark start time!"
        )
        sys.exit(1)
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)
    time.sleep(2)
    logger.info("Starting benchmark")
    press("3")

    test_start_time = int(time.time())
    time.sleep(180)

    test_end_time = int(time.time())
    time.sleep(2)
    press("1")

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)

    # Open quick menu
    press("escape")

    result = find_word("options", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the options menu. Did the game open the quick dialog menu properly?"
        )
        sys.exit(1)

    # Navigate to options menu
    click(result["x"], result["y"])

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "general.png")

    result = find_word("graphics", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the graphics menu. Did the game navigate to the general settings correctly?"
        )
        sys.exit(1)

    # Navigate to graphics menu
    click(result["x"], result["y"])

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_1.png")

    result = find_word("window", timeout=10, interval=1)
    if not result:
        logger.info(
            "Did not find the keyword 'window' in graphics menu. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)

    move_mouse(result["x"], result["y"])
    time.sleep(0.2)

    scroll(-800, 8)

    if find_word(word="water", timeout=30, interval=1) is None:
        logger.info(
            "Did not find the keyword 'water' in menu. Did the game scroll correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_2.png")

    scroll(-400, 8)

    # verify that we scrolled through the menu correctly
    if find_word(word="texture", timeout=30, interval=1) is None:
        logger.info(
            "Did not find the keyword 'texture' in menu. Did the game scroll correctly?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_3.png")
    copy_artifact(CONFIG_FULL_PATH, ARTIFACTS_DIRECTORY)

    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


def main():
    """Run the benchmark and write its report."""
    test_start_time, test_end_time = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)


if __name__ == "__main__":
    try:
        setup_logging(LOG_DIRECTORY)
        main()
    except Exception:
        logger.error("Something went wrong running the benchmark!")
        logger.exception("Unhandled exception")
        terminate_process(PROCESS_NAME)
        sys.exit(1)
