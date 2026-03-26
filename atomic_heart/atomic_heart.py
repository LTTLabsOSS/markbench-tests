"""Atomic Heart test script."""

import logging
import os
import sys
import time
from pathlib import Path

from atomic_heart_utils import read_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.misc import remove_files
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    exec_steam_run_command,
    get_app_install_location,
    get_build_id,
)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\AtomicHeart\\Saved\\Config\\WindowsNoEditor"
CONFIG_FILENAME = "GameUserSettings.ini"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
PROCESS_NAME = "AtomicHeart"
STEAM_GAME_ID = 668580
VIDEO_PATH = (
    Path(get_app_install_location(STEAM_GAME_ID)) / "AtomicHeart" / "Content" / "Movies"
)

intro_videos = [
    VIDEO_PATH / "Launch_4k_60FPS_PS5.mp4",
    VIDEO_PATH / "Launch_4k_60FPS_XboxXS.mp4",
    VIDEO_PATH / "Launch_FHD_30FPS_PS4.mp4",
    VIDEO_PATH / "Launch_FHD_30FPS_XboxOne.mp4",
    VIDEO_PATH / "Launch_FHD_60FPS_PC_Steam.mp4",
]


def launch_game() -> None:
    """Handle pre-launch setup and game launch."""
    remove_files([str(path) for path in intro_videos])
    exec_steam_run_command(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Start the benchmark."""
    launch_game()
    time.sleep(10)

    if not find_word("press", timeout=25, msg="Did not see start screen"):
        return FAILED_RUN

    setup_start_time = int(time.time())
    press("space")

    if find_word("continue", timeout=20, interval=1):
        logging.info("Continue option available, navigating accordingly.")
        press("s*3, f")
        time.sleep(0.5)
    else:
        logging.info("Continue option not available, navigating accordingly.")
        press("s, f")
        time.sleep(0.5)

    if not find_word(
        "vsync",
        timeout=25,
        msg="Did not see display menu. Did we navigate to the options correctly?",
    ):
        return FAILED_RUN
    am.take_screenshot("01_display.png", ArtifactType.CONFIG_IMAGE)

    press("e")
    time.sleep(0.5)
    if not find_word(
        "dlss",
        timeout=25,
        msg="Did not see the top of quality menu. Did we navigate to the quality menu correctly?",
    ):
        return FAILED_RUN
    am.take_screenshot("02_quality_1.png", ArtifactType.CONFIG_IMAGE)

    press("w")
    time.sleep(0.5)
    if not find_word(
        "vegetation",
        timeout=25,
        msg="Did not see the bottom of quality menu. Did we scroll the quality menu correctly?",
    ):
        return FAILED_RUN
    am.take_screenshot("03_quality_2.png", ArtifactType.CONFIG_IMAGE)
    press("esc")
    time.sleep(0.5)

    if find_word("continue", timeout=1):
        press("s, d, f, space")
    else:
        press("s, w, d, f, space")

    time.sleep(10)

    if not find_word(
        "continue",
        interval=1,
        timeout=80,
        msg="Did not see the option to continue. Check settings and try again.",
    ):
        return FAILED_RUN

    press("space")
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word(
        "vibes",
        interval=0.5,
        timeout=250,
        msg="Good vibes were not found! Could not mark the start time.",
    ):
        return FAILED_RUN

    test_start_time = int(time.time())
    time.sleep(216)

    if not find_word(
        "83",
        interval=0.5,
        timeout=250,
        msg="Waypoint distance was not found! Could not mark the end time.",
    ):
        return FAILED_RUN

    test_end_time = int(time.time())
    time.sleep(13)

    if not find_word(
        "wicked",
        interval=1,
        timeout=250,
        msg="Wicked was not found! Did harness not wait long enough? Or test was too long?",
    ):
        return FAILED_RUN

    am.copy_file(CONFIG_FULL_PATH, ArtifactType.CONFIG_TEXT, "GameUserSettings.ini")
    logging.info("Benchmark took %f seconds", round(test_end_time - test_start_time, 2))
    return test_start_time, test_end_time


def main() -> None:
    """Run the Atomic Heart benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = read_resolution()
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
            }
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        exit_code = 1
    finally:
        terminate_processes(PROCESS_NAME)
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
