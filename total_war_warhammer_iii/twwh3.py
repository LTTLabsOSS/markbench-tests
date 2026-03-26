"""Total War: Warhammer III test script."""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import pyautogui as gui
from twwh3_utils import read_current_resolution

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
from harness_utils.steam import get_app_install_location, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "Warhammer3.exe"
STEAM_GAME_ID = 1142710

APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Warhammer3\\scripts"
CONFIG_FILENAME = "preferences.script.txt"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"


def launch_game() -> None:
    cmd_string = f'start /D "{get_app_install_location(STEAM_GAME_ID)}" {PROCESS_NAME}'
    logging.info(cmd_string)
    os.system(cmd_string)


def click_result(result: dict) -> None:
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()


def run_benchmark(am: ArtifactManager, benchmark: str) -> tuple[int, int]:
    """Start the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(5)

    if not find_word("warning", timeout=50, interval=5, msg="Did not see warnings. Did the game start?"):
        return FAILED_RUN
    press("escape*7")
    time.sleep(2)

    result = find_word("options", timeout=10, interval=1, msg="Did not find the options menu. Did the game skip the intros?")
    if not result:
        return FAILED_RUN
    click_result(result)
    time.sleep(2)
    am.take_screenshot("01_main.png", ArtifactType.CONFIG_IMAGE)

    result = find_word("ad", timeout=10, interval=1, msg="Did not find the advanced menu. Did the game skip the intros?")
    if not result:
        return FAILED_RUN
    click_result(result)
    time.sleep(0.5)
    am.take_screenshot("02_advanced.png", ArtifactType.CONFIG_IMAGE)

    result = find_word("bench", timeout=10, interval=1, msg="Did not find the benchmark menu. Did the game skip the intros?")
    if not result:
        return FAILED_RUN
    click_result(result)
    if benchmark != "battle":
        result = find_word("mirrors", timeout=10, interval=1)
        if result:
            click_result(result)
    time.sleep(2)
    press("enter")
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("fps", interval=0.5, timeout=100, msg="Could not find FPS. Unable to mark start time!"):
        return FAILED_RUN
    test_start_time = int(time.time())
    time.sleep(65 if benchmark != "battle" else 100)

    if not find_word("summary", interval=0.2, timeout=250, msg="Results screen was not found! Did harness not wait long enough? Or test was too long?"):
        return FAILED_RUN

    test_end_time = int(time.time()) - 1
    time.sleep(5)
    am.take_screenshot("03_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(Path(CONFIG_FULL_PATH), ArtifactType.RESULTS_TEXT, "preferences.script.txt")
    return test_start_time, test_end_time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--benchmark", dest="benchmark", metavar="benchmark", required=True)
    args = parser.parse_args()

    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0
    try:
        start_time, end_time = run_benchmark(am, args.benchmark)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = read_current_resolution()
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
