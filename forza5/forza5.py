"""Forza Horizon 5 test script"""

import logging
import os
import sys
import time
from argparse import ArgumentParser

import pyautogui as gui
import pydirectinput as user
from forza5_utils import read_resolution

sys.path.insert(1, os.path.join(sys.path[0], "../.."))

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import KerasService
from harness_utils.misc import press_n_times
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command

STEAM_GAME_ID = 1551360
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIR, "run")
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
    profile_path = os.path.join(SCRIPT_DIR, "ForzaHorizon5.exe.cfg")
    copy_rtss_profile(profile_path)
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
        logging.info("Game didn't start.")
        sys.exit(1)

    logging.info("Accessibility found pressing X to continue.")
    user.press("x")
    time.sleep(2)

    result = kerasService.wait_for_word("video", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Video found, clicking and continuing.")
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    am.take_screenshot("Video_pt.png", ArtifactType.CONFIG_IMAGE, "Video menu")
    time.sleep(0.2)
    press_n_times("down", 19, 0.1)
    am.take_screenshot("Video_pt2.png", ArtifactType.CONFIG_IMAGE, "Video menu2")
    press_n_times("down", 5, 0.1)
    am.take_screenshot("Video_pt3.png", ArtifactType.CONFIG_IMAGE, "Video menu3")
    time.sleep(0.2)
    user.press("escape")
    time.sleep(1)

    result = kerasService.wait_for_word("graphics", timeout=30)
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
    am.take_screenshot("graphics_pt.png", ArtifactType.CONFIG_IMAGE, "graphics menu")
    time.sleep(0.2)
    press_n_times("down", 16, 0.1)
    am.take_screenshot("graphics_pt2.png", ArtifactType.CONFIG_IMAGE, "graphics menu2")
    time.sleep(0.1)
    user.press("down")
    time.sleep(1)

    result = kerasService.wait_for_word("benchmark", timeout=12)
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

    result = kerasService.wait_for_word("checkpoint", timeout=360)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    elapsed_setup_time = round((int(time.time()) - setup_start_time), 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)

    test_start_time = int(time.time())

    time.sleep(95)  # wait for benchmark to finish 95 seconds

    result = kerasService.wait_for_word("results", timeout=25)
    if not result:
        logging.info("Results screen was not found!")
        sys.exit(1)

    test_end_time = int(time.time())
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    terminate_processes(*PROCESSES)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(
    filename=f"{LOG_DIRECTORY}/harness.log",
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG,
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

parser = ArgumentParser()
parser.add_argument(
    "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True
)
parser.add_argument(
    "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True
)
args = parser.parse_args()
kerasService = KerasService()
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
