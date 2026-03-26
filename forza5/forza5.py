"""Forza Horizon 5 test script."""

import logging
import os
import sys
import time
from pathlib import Path

import pyautogui as gui
from forza5_utils import read_resolution

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
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command

STEAM_GAME_ID = 1551360
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
APPDATALOCAL = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = (
    f"{APPDATALOCAL}\\ForzaHorizon5\\User_SteamLocalStorageDirectory"
    "\\ConnectedStorage\\ForzaUserConfigSelections"
)
CONFIG_FILENAME = "UserConfigSelections"
PROCESSES = ["ForzaHorizon5.exe", "RTSS.exe"]


def launch_game() -> None:
    """Handle pre-launch setup and game launch."""
    profile_path = SCRIPT_DIRECTORY / "ForzaHorizon5.exe.cfg"
    copy_rtss_profile(str(profile_path))
    start_rtss_process()
    time.sleep(10)
    exec_steam_run_command(STEAM_GAME_ID)


def click_result(result: dict) -> None:
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Start the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(30)

    if not find_word("start", timeout=30, msg="Game didn't start."):
        return FAILED_RUN

    press("x")
    time.sleep(2)

    result = find_word("video", timeout=30, msg="Game didn't load to the settings menu.")
    if not result:
        return FAILED_RUN
    click_result(result)
    am.take_screenshot("01_video_1.png", ArtifactType.CONFIG_IMAGE)
    press("down*19", pause=0.1)
    am.take_screenshot("02_video_2.png", ArtifactType.CONFIG_IMAGE)
    press("down*5", pause=0.1)
    am.take_screenshot("03_video_3.png", ArtifactType.CONFIG_IMAGE)
    press("escape")
    time.sleep(1)

    result = find_word("graphics", timeout=30, msg="Game didn't load to the settings menu.")
    if not result:
        return FAILED_RUN
    click_result(result)
    am.take_screenshot("04_graphics_1.png", ArtifactType.CONFIG_IMAGE)
    press("down*16", pause=0.1)
    am.take_screenshot("05_graphics_2.png", ArtifactType.CONFIG_IMAGE)
    press("down")
    time.sleep(1)

    result = find_word("benchmark", timeout=12, msg="Didn't find benchmark in settings.")
    if not result:
        return FAILED_RUN
    gui.mouseDown(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(1)
    press("down, enter")

    if not find_word("checkpoint", timeout=360, msg="Benchmark didn't start."):
        return FAILED_RUN

    logging.info("Harness setup took %.2f seconds", round(int(time.time()) - setup_start_time, 2))
    test_start_time = int(time.time())
    time.sleep(95)

    if not find_word("results", timeout=25, msg="Results screen was not found!"):
        return FAILED_RUN

    test_end_time = int(time.time())
    logging.info("Benchmark took %.2f seconds", round(test_end_time - test_start_time, 2))
    return test_start_time, test_end_time


def main() -> None:
    """Run the Forza Horizon 5 benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            width, height = read_resolution(f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}")
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
            }
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        exit_code = 1
    finally:
        terminate_processes(*PROCESSES)
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
