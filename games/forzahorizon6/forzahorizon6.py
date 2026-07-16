"""Forza Horizon 6 test script"""

import logging
import sys
import time
from pathlib import Path

from forzahorizon6_utils import read_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import reset_artifacts, save_screenshot
from harness_utils.input import mangohud_log_toggle, press_n_times, user
from harness_utils.ocr_service import find_word
from harness_utils.report import format_resolution, seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, local_appdata
from harness_utils.platform import is_linux, is_windows
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game

STEAM_GAME_ID = 2483190
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "ForzaHorizon6.exe"
RTSS_PROCESS_NAME = "RTSS.exe"

user.FAILSAFE = False


def get_config_path() -> Path:
    """Returns the Forza Horizon 6 user config path."""
    return (
        local_appdata(STEAM_GAME_ID)
        / "ForzaHorizon6"
        / "LocalStorage_Shared"
        / "ForzaUserConfigSelections"
        / "UserConfigSelections"
    )


def start_rtss():
    """Sets up the RTSS process"""
    if not is_windows():
        logging.info("Skipping RTSS setup on Linux.")
        return None

    from harness_utils.rtss import copy_rtss_profile, start_rtss_process

    profile_path = SCRIPT_DIRECTORY / "ForzaHorizon6.exe.cfg"
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
    time.sleep(40)

    logging.info("Waiting for start prompt...")
    result = find_word("start", timeout=30)
    if not result:
        logging.info("Did not see 'start'. Game didn't start.")
        sys.exit(1)

    user.move_mouse(0, 0)
    user.click()

    if is_linux():
        mangohud_log_toggle()

    logging.info("At main menu. Pressing x for options.")
    user.press("x")

    # Wait for menu to load
    result = find_word("subtitles", timeout=10)
    if not result:
        logging.info("Did not see 'subtitles'. Menu did not open?")
        sys.exit(1)

    # Menu defaults to accessibility submenu, so we need to escape first.
    user.press("escape")
    time.sleep(1)

    result = find_word("video", timeout=30)
    if not result:
        logging.info("Did not see 'video'. Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Video found, selecting with keyboard.")
    press_n_times("down", 6, 1)
    time.sleep(1)
    user.press("enter")
    save_screenshot(ARTIFACTS_DIRECTORY / "Video_pt.png")
    time.sleep(1)

    press_n_times("down", 21, 1)
    save_screenshot(ARTIFACTS_DIRECTORY / "Video_pt2.png")
    user.press("escape")
    time.sleep(1)

    result = find_word("graphics", timeout=30)
    if not result:
        logging.info("Game didn't load to the settings menu.")
        sys.exit(1)

    logging.info("Graphics found, selecting with keyboard.")
    user.press("down")
    time.sleep(1)
    user.press("enter")
    time.sleep(1)
    save_screenshot(ARTIFACTS_DIRECTORY / "graphics_pt.png")
    press_n_times("down", 18, 1)
    save_screenshot(ARTIFACTS_DIRECTORY / "graphics_pt2.png")
    time.sleep(1)
    user.press("down")
    time.sleep(1)

    result = find_word("benchmark", timeout=10)
    if not result:
        logging.info("Didn't find benchmark in settings.")
        sys.exit(1)

    logging.info("Benchmark found, selecting with keyboard.")
    user.press("enter")

    result = find_word("yes", timeout=10)
    if not result:
        logging.info("Didn't find confirmation prompt.")
        sys.exit(1)

    logging.info("Confirmation prompt found, selecting yes with keyboard.")
    user.press("down")
    time.sleep(1)
    user.press("enter")

    result = find_word("checkpoint", timeout=60)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    elapsed_setup_time = round((int(time.time()) - setup_start_time), 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)

    test_start_time = int(time.time())

    time.sleep(60)  # wait for benchmark to finish

    result = find_word("results", timeout=30)
    if not result:
        logging.info("Results screen was not found!")
        sys.exit(1)

    test_end_time = int(time.time())
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    if is_linux():
        mangohud_log_toggle()
        user.move_mouse(0, 0)

    terminate_game_processes()
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)
reset_artifacts(ARTIFACTS_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    width, height = read_resolution(get_config_path())
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_game_processes()
    sys.exit(1)
