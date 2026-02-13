"""Forza Motorsport test script"""

import logging
import os
import sys
import time

from forzamotorsport_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], "../.."))

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import KerasService
from harness_utils.misc import press_n_times
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command, get_build_id

STEAM_GAME_ID = 2440510
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
LOCAL_USER_SETTINGS = os.path.join(
    os.getenv("LOCALAPPDATA"),
    "Microsoft.ForzaMotorsport",
    "User_SteamLocalStorageDirectory",
    "ConnectedStorage",
    "ForzaUserConfigSelections",
    "UserConfigSelections",
)
PROCESSES = ["forza_steamworks_release_final.exe", "RTSS.exe"]

user.FAILSAFE = False


def start_rtss():
    """Sets up the RTSS process"""
    profile_path = os.path.join(
        SCRIPT_DIRECTORY, "forza_steamworks_release_final.exe.cfg"
    )
    copy_rtss_profile(profile_path)
    return start_rtss_process()


def run_benchmark() -> tuple[float]:
    """Run the benchmark"""
    start_rtss()
    # Give RTSS time to start
    time.sleep(10)
    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    am = ArtifactManager(LOG_DIRECTORY)

    time.sleep(50)

    # Make sure the game started correctly
    if kerasService.wait_for_word(word="play", timeout=30, interval=1) is None:
        logging.info("Could not find the main menu. Did the game load?")
        sys.exit(1)

    # Navigate to display menu
    user.press("f")
    time.sleep(1)

    if kerasService.wait_for_word(word="contrast", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the accessibility settings menu. Did the menu get stuck?"
        )
        sys.exit(1)

    user.press("]")
    time.sleep(0.5)
    user.press("]")
    time.sleep(0.5)
    user.press("]")
    time.sleep(0.5)

    # Verify that we have navigated to the video settings menu and take a screenshot
    if kerasService.wait_for_word(word="resolution", timeout=30, interval=1) is None:
        logging.info("Did not find the display settings menu. Did the menu get stuck?")
        sys.exit(1)

    am.take_screenshot(
        "display.png", ArtifactType.CONFIG_IMAGE, "picture of display settings"
    )
    user.press("]")
    time.sleep(0.5)

    if kerasService.wait_for_word(word="filtering", timeout=30, interval=1) is None:
        logging.info("Did not find the graphics settings menu. Did the menu get stuck?")
        sys.exit(1)
    am.take_screenshot(
        "graphics1.png", ArtifactType.CONFIG_IMAGE, "1st picture of graphics settings"
    )

    press_n_times("down", 15, 0.5)

    if kerasService.wait_for_word(word="particle", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the particle effect settings. Did the menu get stuck?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics2.png", ArtifactType.CONFIG_IMAGE, "2nd picture of graphics settings"
    )

    press_n_times("down", 3, 0.5)
    user.press("up")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)

    if kerasService.wait_for_word(word="flare", timeout=30, interval=1) is None:
        logging.info("Did not find the lens flare settings. Did the menu get stuck?")
        sys.exit(1)
    am.take_screenshot(
        "graphics3.png", ArtifactType.CONFIG_IMAGE, "3rd picture of graphics settings"
    )

    # Navigate to graphics menu
    user.press("[")
    time.sleep(0.5)
    user.press("enter")

    setup_end_time = int(time.time())
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logging.info("Setup took %s seconds", elapsed_setup_time)

    time.sleep(15)

    if kerasService.wait_for_word(word="results", timeout=60, interval=0.5) is None:
        logging.info("Did not find the results screen. Did the game load?")
        sys.exit(1)
    am.take_screenshot(
        "results.png", ArtifactType.CONFIG_IMAGE, "picture of results screen"
    )

    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(180)

    # Wait for results screen to display info
    if kerasService.wait_for_word(word="results", timeout=15, interval=0.5) is None:
        logging.info(
            "Did not find the results screen. Did the game crash during the run?"
        )
        sys.exit(1)

    test_end_time = round(int(time.time()))
    # Give results screen time to fill out, then save screenshot and config file
    time.sleep(2)
    am.copy_file(LOCAL_USER_SETTINGS, ArtifactType.CONFIG_TEXT, "config file")

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %s seconds", elapsed_test_time)

    terminate_processes(*PROCESSES)
    am.create_manifest()

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

kerasService = KerasService()

try:
    start_time, end_time = run_benchmark()
    resolution = get_resolution(LOCAL_USER_SETTINGS)
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(*PROCESSES)
    sys.exit(1)
