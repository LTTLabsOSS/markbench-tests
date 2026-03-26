"""Grid Legends test script."""

import logging
import os
import re
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "gridlegends.exe"
STEAM_GAME_ID = 1307710

username = os.getlogin()
CONFIG_PATH = (
    f"C:\\Users\\{username}\\Documents\\My Games\\GRID Legends\\hardwaresettings"
)
CONFIG_FILENAME = "hardware_settings_config.xml"
CONFIG_FULL_PATH = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"


def get_resolution() -> tuple[int]:
    """Get resolution width and height from local xml file."""
    resolution = re.compile(r"<resolution width=\"(\d+)\" height=\"(\d+)\"")
    height = 0
    width = 0
    with open(CONFIG_FULL_PATH, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = resolution.search(line)
            width_match = resolution.search(line)
            if height_match is not None:
                height = height_match.group(2)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)


def launch_game() -> None:
    exec_steam_game(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run Grid Legends benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(20)

    if not find_word("press", timeout=80, interval=1, msg="Game didn't load to start screen. Did the game load?"):
        return FAILED_RUN

    logging.info("Game started. Entering main menu")
    time.sleep(4)
    press("enter")
    time.sleep(2)

    if not find_word("home", timeout=80, interval=1, msg="Game didn't load to main menu. Check settings and try again."):
        return FAILED_RUN

    logging.info("Starting benchmark")
    press("f3, right, right, enter")

    if not find_word("basic", timeout=30, interval=0.1, msg="Didn't basic video options. Did the menu navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot("01_basic.png", ArtifactType.CONFIG_IMAGE)

    press("f3")
    if not find_word("benchmark", timeout=30, interval=0.1, msg="Didn't reach advanced video options. Did the menu navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot("02_advanced_1.png", ArtifactType.CONFIG_IMAGE)

    press("up")
    if not find_word("shading", timeout=30, interval=0.1, msg="Didn't reach bottom of advanced video settings. Did the menu navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot("03_advanced_2.png", ArtifactType.CONFIG_IMAGE)

    press("down, enter")
    logging.info("Harness setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("manzi", timeout=120, interval=0.1, msg="Didn't see Valentino Manzi. Did the benchmark load?"):
        return FAILED_RUN
    test_start_time = int(time.time())
    time.sleep(136)

    if not find_word(
        "results",
        timeout=30,
        interval=0.1,
        msg="Didn't see results screen for the benchmark. Could not mark start time! Did the benchmark crash?",
    ):
        return FAILED_RUN

    test_end_time = int(time.time()) - 2
    time.sleep(2)
    am.take_screenshot("04_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(Path(CONFIG_FULL_PATH), ArtifactType.CONFIG_TEXT, "game config")
    logging.info("Run completed. Closing game.")
    time.sleep(2)
    return test_start_time, test_end_time


def main() -> None:
    """Run the Grid Legends benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            logging.info("Benchmark took %f seconds", round((end_time - start_time), 2))
            height, width = get_resolution()
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
            }
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
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
