"""Shadow of the Tomb Raider test script"""

import logging
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
from harness_utils.input import mangohud_log_toggle, user
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, user_documents
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.registry import read_registry_value
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import exec_steam_game, get_build_id

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 750920
PROCESS_NAME = "SOTTR.exe"
REGISTRY_PATH = r"SOFTWARE\Eidos Montreal\Shadow of the Tomb Raider\Graphics"
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
user.FAILSAFE = False


def get_resolution() -> tuple[int, int]:
    """Get resolution from the registry."""
    width = read_registry_value(
        REGISTRY_PATH, "FullscreenWidth", steam_app_id=STEAM_GAME_ID
    )
    height = read_registry_value(
        REGISTRY_PATH, "FullscreenHeight", steam_app_id=STEAM_GAME_ID
    )
    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("Could not read resolution from the registry")
    return height, width


def get_latest_file_report(directory: Path) -> Path | None:
    """Get the latest benchmark report."""
    files = [
        file
        for file in directory.iterdir()
        if file.is_file() and file.suffix != ".log" and "frametimes" not in file.name
    ]
    return max(files, key=lambda path: path.stat().st_mtime, default=None)


def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-nolauncher"])


def run_benchmark():
    """Start game via Steam and enter fullscreen mode"""
    setup_start_time = int(time.time())
    start_game()
    time.sleep(10)

    # Check for if no display adapter warning is up
    if find_word(word="adapter", timeout=30, interval=1):
        user.press("enter")

    # Check for if notification for services unavailable is up
    if find_word(word="unavailable", timeout=10, interval=1):
        user.press("enter")

    if is_linux():
        mangohud_log_toggle()

    if find_word(word="options", timeout=30, interval=1) is None:
        logger.info("Did not find the options menu. Did the game launch correctly?")
        sys.exit(1)

    logger.info("found options")

    user.press("up")
    time.sleep(0.5)
    user.press("up")
    time.sleep(0.5)
    user.press("up")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1)

    if find_word(word="graphics", timeout=30, interval=1) is None:
        logger.info("Did not find the graphics menu. Did the menu get stuck?")
        sys.exit(1)

    logger.info("found graphics")
    # wait for menu to fully move
    time.sleep(1)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(4)

    if find_word(word="benchmark", timeout=30, interval=1) is None:
        logger.info(
            "Did not find the benchmark option on the screen. Did the menu get stuck?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display.png")

    user.press("up")
    time.sleep(0.5)
    user.press("right")
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics.png")

    user.press("r")
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)

    if find_word(word="fps", timeout=60, interval=0.5) is None:
        logger.info("Did not find the FPS counter. Did the benchmark crash?")
        sys.exit(1)
    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(180)

    test_end_time = int(time.time())

    result = find_word(word="tomb", timeout=10, interval=0.1)
    if result is None:
        logger.error("Unable to find the loading screen. Using default end time value.")
    else:
        test_end_time = int(time.time())

    if find_word(word="results", timeout=60, interval=1) is None:
        logger.error("Results screen after running benchmark not found, exiting.")
        sys.exit(1)

    logger.info("Run completed. Closing game.")

    time.sleep(2)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")

    game_document_dir = user_documents(STEAM_GAME_ID) / "Shadow of the Tomb Raider"
    game_log = game_document_dir.joinpath("Shadow of the Tomb Raider.log")
    copy_artifact(game_log, ARTIFACTS_DIRECTORY)
    latest_report = get_latest_file_report(game_document_dir)
    if latest_report is None or latest_report.stat().st_mtime < test_start_time:
        raise FileNotFoundError("Could not find the benchmark report")
    copy_artifact(latest_report, ARTIFACTS_DIRECTORY)

    terminate_process(PROCESS_NAME)
    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)


def main():
    """entry point"""
    setup_logging(LOG_DIRECTORY)
    run_benchmark()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.error("Something went wrong running the benchmark!")
        logger.exception("Unhandled exception")
        terminate_process(PROCESS_NAME)
        sys.exit(1)
