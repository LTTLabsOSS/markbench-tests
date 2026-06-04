"""Forza Horizon 6 test script"""

import logging
import os
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from forzahorizon6_utils import read_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import KerasService
from harness_utils.misc import press_n_times, clickme
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command

STEAM_GAME_ID = 2483190
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
APPDATALOCAL = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATALOCAL}\\ForzaHorizon6\\LocalStorage_Shared\\ForzaUserConfigSelections"
CONFIG_FILENAME = "UserConfigSelections"
PROCESSES = ["ForzaHorizon6.exe", "RTSS.exe"]

user.FAILSAFE = False

def start_rtss():
    """Sets up the RTSS process"""
    profile_path = SCRIPT_DIRECTORY / "ForzaHorizon6.exe.cfg"
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
    result = kerasService.wait_for_word("start", timeout=30)
    if not result:
        logging.info("Did not see 'start'. Game didn't start.")
        sys.exit(1)

    logging.info("At main menu. Pressing x for options.")
    user.press("x")

    # Wait for menu to load
    result = kerasService.wait_for_word("subtitles", timeout=10)
    if not result:
        logging.info("Did not see 'subtitles'. Menu did not open?")
        sys.exit(1)

    # Menu defaults to accessibility submenu, so we need to escape first.
    user.press("escape")
    time.sleep(0.5)

    result = kerasService.wait_for_word("video", timeout=30)
    if not result:
        logging.info("Did not see 'video'. Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Video found, clicking and continuing.")
    clickme(result["x"], result["y"])
    am.take_screenshot("Video_pt.png", ArtifactType.CONFIG_IMAGE, "Video menu")
    time.sleep(0.2)

    press_n_times("down", 20, 0.1)
    am.take_screenshot("Video_pt2.png", ArtifactType.CONFIG_IMAGE, "Video menu2")
    user.press("escape")
    time.sleep(0.5)

    result = kerasService.wait_for_word("graphics", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Graphics found, clicking and continuing.")
    clickme(result["x"], result["y"])
    time.sleep(0.2)
    am.take_screenshot("graphics_pt.png", ArtifactType.CONFIG_IMAGE, "graphics menu")
    press_n_times("down", 18, 0.1)
    am.take_screenshot("graphics_pt2.png", ArtifactType.CONFIG_IMAGE, "graphics menu2")
    time.sleep(0.2)
    user.press("down")

    result = kerasService.wait_for_word("benchmark", timeout=10)
    if not result:
        logging.info("Didn't find benchmark in settings.")
        sys.exit(1)

    clickme(result["x"], result["y"])

    result = kerasService.wait_for_word("yes", timeout=10)
    clickme(result["x"], result["y"])

    result = kerasService.wait_for_word("checkpoint", timeout=60)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    elapsed_setup_time = round((int(time.time()) - setup_start_time), 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)

    test_start_time = int(time.time())

    time.sleep(60)  # wait for benchmark to finish 95 seconds

    result = kerasService.wait_for_word("results", timeout=30)
    if not result:
        logging.info("Results screen was not found!")
        sys.exit(1)

    test_end_time = int(time.time())
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    terminate_processes(*PROCESSES)
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

parser = ArgumentParser()
parser.add_argument(
    "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True
)
parser.add_argument(
    "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True
)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port)
am = ArtifactManager(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    width, height = read_resolution(f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}")
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }
    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(*PROCESSES)
    sys.exit(1)
