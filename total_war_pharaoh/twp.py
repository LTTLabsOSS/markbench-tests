"""Total War: Pharaoh test script."""

import logging
import os
import re
import sys
import time
from pathlib import Path

import pyautogui as gui

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.misc import mouse_scroll_n_times
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
PROCESS_NAME = "Pharaoh.exe"
STEAM_GAME_ID = 1937780
APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Pharaoh\\scripts"
CONFIG_FILENAME = "preferences.script.txt"


def read_current_resolution():
    height_pattern = re.compile(r"y_res (\d+);")
    width_pattern = re.compile(r"x_res (\d+);")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        for line in file.readlines():
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


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


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(5)

    if not find_word("warning", timeout=50, interval=5, msg="Did not see warnings. Did the game start?"):
        return FAILED_RUN
    press("escape*4")
    time.sleep(2)

    result = find_word("options", timeout=10, interval=1, msg="Did not find the options menu. Did the game skip the intros?")
    if not result:
        return FAILED_RUN
    click_result(result)

    if not find_word("brightness", timeout=30, interval=1, msg="Did not find the main menu. Did OCR click correctly?"):
        return FAILED_RUN
    am.take_screenshot("01_main.png", ArtifactType.CONFIG_IMAGE)

    result = find_word("advanced", timeout=10, interval=1, msg="Did not find the advanced options menu.")
    if not result:
        return FAILED_RUN
    click_result(result)

    if not find_word("water", timeout=30, interval=1, msg="Did not find the keyword 'water' in the menu."):
        return FAILED_RUN
    am.take_screenshot("02_advanced_1.png", ArtifactType.CONFIG_IMAGE)
    mouse_scroll_n_times(15, -1, 0.1)
    if not find_word("heat", timeout=30, interval=1, msg="Did not find the keyword 'heat' in the menu."):
        return FAILED_RUN
    am.take_screenshot("03_advanced_2.png", ArtifactType.CONFIG_IMAGE)
    mouse_scroll_n_times(15, -1, 0.1)
    if not find_word("bodies", timeout=30, interval=1, msg="Did not find the keyword 'bodies' in the menu."):
        return FAILED_RUN
    am.take_screenshot("04_advanced_3.png", ArtifactType.CONFIG_IMAGE)

    result = find_word("bench", timeout=10, interval=1, msg="Did not find the benchmark menu. Did the game skip the intros?")
    if not result:
        return FAILED_RUN
    click_result(result)
    time.sleep(2)
    press("enter")
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("fps", interval=0.5, timeout=100, msg="Could not find FPS. Unable to mark start time!"):
        return FAILED_RUN
    test_start_time = int(time.time()) - 2
    time.sleep(90)
    if not find_word("summary", interval=0.2, timeout=250, msg="Results screen was not found! Did harness not wait long enough? Or test was too long?"):
        return FAILED_RUN
    test_end_time = int(time.time()) - 1
    time.sleep(5)
    am.take_screenshot("05_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(Path(cfg), ArtifactType.CONFIG_TEXT, "preferences.script.txt")
    return test_start_time, test_end_time


def main() -> None:
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0
    try:
        start_time, end_time = run_benchmark(am)
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
