"""Counter-Strike 2 test script"""

import logging
import sys
import time
from pathlib import Path

from counter_strike_2_utils import get_resolution

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
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import (
    exec_steam_game,
    get_active_steam_account_id,
    get_build_id,
    get_steam_folder_path,
)

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "cs2.exe"
STEAM_GAME_ID = 730

STEAM_USER_ID = get_active_steam_account_id()
CFG = Path(
    get_steam_folder_path(),
    "userdata",
    str(STEAM_USER_ID),
    str(STEAM_GAME_ID),
    "local",
    "cfg",
    "cs2_video.txt",
)


def run_benchmark():
    exec_steam_game(
        STEAM_GAME_ID, game_params=["-console", "-fullscreen", "+fps_max 0"]
    )

    time.sleep(30)

    if not find_word(word="loadout", timeout=30, interval=1):
        raise RuntimeError(
            "Did not find loadout to verify that the game has loaded to the main menu"
        )

    time.sleep(10)

    height, width = get_resolution()

    if width <= 0 or height <= 0:
        raise RuntimeError(
            f"Cannot click settings with invalid resolution: {width}x{height}"
        )

    click(round(width * 0.13), round(height * 0.03))

    time.sleep(5)

    click(round(width * 0.0625), round(height * 0.03))

    time.sleep(2)

    result = find_word(word="video", timeout=10, interval=1)
    if not result:
        raise RuntimeError("Did not find video to find the video menu button")

    click(result["x"], result["y"])

    time.sleep(2)

    if not find_word(word="brightness", timeout=30, interval=1):
        raise RuntimeError("Did not find brightness to find the video settings")

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video.png")

    result = find_word(word="advanced", timeout=10, interval=1)
    if not result:
        raise RuntimeError("Did not find advanced to find the advanced video menu")

    click(result["x"], result["y"])

    time.sleep(2)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "advanced_video_1.png")

    result = find_word(word="boost", timeout=10, interval=1)
    if not result:
        raise RuntimeError(
            "Did not find boost to identify we're in the advanced video menu"
        )

    move_mouse(result["x"], result["y"])
    time.sleep(1)
    scroll(-600)
    time.sleep(1)

    if not find_word(word="particle", timeout=30, interval=1):
        raise RuntimeError("Did not find particle to verify we scrolled correctly")

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "advanced_video_2.png")

    logger.info("Starting benchmark")

    result = find_word(word="play", timeout=10, interval=1)
    if not result:
        raise RuntimeError("Did not find play to click the play tab")

    click(result["x"], result["y"])

    result = find_word(word="workshop", timeout=10, interval=1)
    if not result:
        raise RuntimeError("Did not find workshop to click the workshop tab")

    click(result["x"], result["y"])

    result = find_word(word="fps", timeout=10, interval=1)
    if not result:
        raise RuntimeError("Did not find fps to click the benchmark icon")

    click(result["x"], result["y"])

    result = find_word(word="go", timeout=10, interval=1)
    if not result:
        raise RuntimeError("Did not find go to start the benchmark")

    click(result["x"], result["y"])

    time.sleep(3)

    if not find_word(word="benchmark", timeout=30, interval=1):
        raise RuntimeError(
            "Did not find benchmark to verify that the benchmark has started"
        )

    time.sleep(1)

    # Default fallback start time
    test_start_time = int(time.time())

    if find_word(word="roll", timeout=30, interval=0.1) is None:
        logger.error("Didn't see 'lets roll'. Did the map load?")
    else:
        test_start_time = int(time.time())
        logger.info("Saw 'lets roll'! Marking the time.")

    time.sleep(112)  # sleep duration during gameplay

    # Default fallback end time
    test_end_time = int(time.time())

    if not find_word(word="console", timeout=30, interval=1):
        raise RuntimeError(
            "Did not find console to verify the console has opened to show the results"
        )

    test_end_time = int(time.time())

    press("`")

    time.sleep(13)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    copy_artifact(CFG, ARTIFACTS_DIRECTORY)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


def main():
    try:
        setup_logging(LOG_DIRECTORY)
        start_time, end_time = run_benchmark()

        height, width = get_resolution()
        report = {
            "resolution": format_resolution(width, height),
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
            "version": get_build_id(STEAM_GAME_ID),
        }

        write_report_json(LOG_DIRECTORY, "report.json", report)
        create_artifacts_manifest(ARTIFACTS_DIRECTORY)
    except Exception:
        logger.error("something went wrong running the benchmark!")
        logger.exception("Unhandled exception")
        sys.exit(1)
    finally:
        terminate_process(PROCESS_NAME)


if __name__ == "__main__":
    main()
