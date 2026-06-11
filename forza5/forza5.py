"""Forza Horizon 5 test script"""

import logging
import sys
import time
from pathlib import Path

from forza5_utils import read_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.input import mangohud_log_toggle, press_n_times, user
from harness_utils.ocr_service import find_word
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.paths import local_appdata
from harness_utils.platform import is_linux, is_windows
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game

STEAM_GAME_ID = 1551360
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "ForzaHorizon5.exe"
RTSS_PROCESS_NAME = "RTSS.exe"

user.FAILSAFE = False


def get_config_path() -> Path:
    """Returns the Forza Horizon 5 user config path."""
    return (
        local_appdata(STEAM_GAME_ID)
        / "ForzaHorizon5"
        / "User_SteamLocalStorageDirectory"
        / "ConnectedStorage"
        / "ForzaUserConfigSelections"
        / "UserConfigSelections"
    )


def start_rtss():
    """Sets up the RTSS process"""
    if not is_windows():
        logging.info("Skipping RTSS setup on Linux.")
        return None

    from harness_utils.rtss import copy_rtss_profile, start_rtss_process

    profile_path = SCRIPT_DIRECTORY / "ForzaHorizon5.exe.cfg"
    copy_rtss_profile(str(profile_path))
    return start_rtss_process()


def terminate_game_processes():
    """Terminates the game and any Windows-only helper processes."""
    terminate_process(PROCESS_NAME)
    if is_windows():
        terminate_process(RTSS_PROCESS_NAME)


def run_benchmark():
    """Starts the benchmark"""
    if start_rtss():
        # Give RTSS time to start
        time.sleep(10)

    exec_steam_game(STEAM_GAME_ID)
    setup_start_time = int(time.time())

    # Wait for menu to load
    time.sleep(30)

    logging.info("Waiting for start prompt...")
    result = find_word("start", timeout=30)
    if not result:
        logging.info("Game didn't start.")
        sys.exit(1)

    if is_linux():
        user.click(0, 0)
        mangohud_log_toggle()

    logging.info("Accessibility found pressing X to continue.")
    user.press("x")
    time.sleep(2)

    result = find_word("video", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Video found, clicking and continuing.")
    user.click(result["x"], result["y"])
    time.sleep(0.5)
    am.take_screenshot("Video_pt.png", ArtifactType.CONFIG_IMAGE, "Video menu")
    time.sleep(0.5)
    press_n_times("down", 19, 0.5)
    am.take_screenshot("Video_pt2.png", ArtifactType.CONFIG_IMAGE, "Video menu2")
    press_n_times("down", 5, 0.5)
    am.take_screenshot("Video_pt3.png", ArtifactType.CONFIG_IMAGE, "Video menu3")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(1)

    result = find_word("graphics", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Graphics found, clicking and continuing.")
    user.click(result["x"], result["y"])
    time.sleep(0.5)
    time.sleep(0.5)
    am.take_screenshot("graphics_pt.png", ArtifactType.CONFIG_IMAGE, "graphics menu")
    time.sleep(0.5)
    press_n_times("down", 16, 0.5)
    am.take_screenshot("graphics_pt2.png", ArtifactType.CONFIG_IMAGE, "graphics menu2")
    time.sleep(0.5)
    user.press("down")
    time.sleep(1)

    result = find_word("benchmark", timeout=12)
    if not result:
        logging.info("Didn't find benchmark in settings.")
        sys.exit(1)

    user.click(result["x"], result["y"])
    time.sleep(1)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(0.5)

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

    if is_linux():
        mangohud_log_toggle()

    terminate_game_processes()
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)
am = ArtifactManager(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    width, height = read_resolution(get_config_path())
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
    terminate_game_processes()
    sys.exit(1)
