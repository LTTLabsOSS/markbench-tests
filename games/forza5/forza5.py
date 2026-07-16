"""Forza Horizon 5 test script"""

import logging
import os
import sys
import time
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from forza5_utils import read_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import capture_and_save_screenshot, reset_artifacts
from harness_utils.paths import harness_directories
from harness_utils.input import press_n_times
from harness_utils.ocr_service import find_word
from harness_utils.report import format_resolution, seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command

STEAM_GAME_ID = 1551360
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
APPDATALOCAL = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = (
    f"{APPDATALOCAL}\\ForzaHorizon5\\User_SteamLocalStorageDirectory"
    "\\ConnectedStorage\\ForzaUserConfigSelections"
)
CONFIG_FILENAME = "UserConfigSelections"
PROCESSES = ["ForzaHorizon5.exe", "RTSS.exe"]

user.FAILSAFE = False


def start_rtss():
    """Sets up the RTSS process"""
    profile_path = SCRIPT_DIRECTORY / "ForzaHorizon5.exe.cfg"
    copy_rtss_profile(str(profile_path))
    return start_rtss_process()


def run_benchmark():
    """Starts the benchmark"""
    start_rtss()
    # Give RTSS time to start
    time.sleep(10)

    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())

    # Wait for menu to load
    time.sleep(30)

    logging.info("Waiting for start prompt...")
    result = find_word("start", timeout=30)
    if not result:
        logging.info("Game didn't start.")
        sys.exit(1)

    logging.info("Accessibility found pressing X to continue.")
    user.press("x")
    time.sleep(2)

    result = find_word("video", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Video found, clicking and continuing.")
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Video_pt.png")
    time.sleep(0.2)
    press_n_times("down", 19, 0.1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Video_pt2.png")
    press_n_times("down", 5, 0.1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Video_pt3.png")
    time.sleep(0.2)
    user.press("escape")
    time.sleep(1)

    result = find_word("graphics", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Graphics found, clicking and continuing.")
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_pt.png")
    time.sleep(0.2)
    press_n_times("down", 16, 0.1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_pt2.png")
    time.sleep(0.1)
    user.press("down")
    time.sleep(1)

    result = find_word("benchmark", timeout=12)
    if not result:
        logging.info("Didn't find benchmark in settings.")
        sys.exit(1)

    gui.mouseDown(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(1)
    user.press("down")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)

    result = find_word("checkpoint", timeout=360)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    elapsed_setup_time = round((int(time.time()) - setup_start_time), 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)

    test_start_time = int(time.time())

    time.sleep(95)  # wait for benchmark to finish 95 seconds

    result = find_word("results", timeout=25)
    if not result:
        logging.info("Results screen was not found!")
        sys.exit(1)

    test_end_time = int(time.time())
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    for proc_name in PROCESSES:
        terminate_process(proc_name)
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

reset_artifacts(ARTIFACTS_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    width, height = read_resolution(f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}")
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for process_name in PROCESSES:
        terminate_process(process_name)
    sys.exit(1)
