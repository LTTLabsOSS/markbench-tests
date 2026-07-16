"""The Last of Us Part I test script"""

import logging
import os
import sys
import time
from pathlib import Path

import pydirectinput as user
from the_last_of_us_part_i_utils import copy_autosave, get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import capture_and_save_screenshot
from harness_utils.paths import harness_directories
from harness_utils.input import press_n_times
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import (
    exec_steam_run_command,
    get_active_steam_account_id,
)

STEAM_GAME_ID = 1888930
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "tlou-i.exe"

user.FAILSAFE = False


def take_screenshots() -> None:
    """Take screenshots of the benchmark settings"""

    logging.info("Taking screenshots of benchmark settings")

    # navigating to the display menu
    result = find_word("options", interval=1, timeout=5)
    if not result:
        logging.info("Did not see main menu. Did something mess up?")
        sys.exit(1)
    press_n_times("s", 2, 0.2)
    user.press("enter")

    result = find_word("display", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see options menu (looking for display). Did something mess up?"
        )
        sys.exit(1)
    press_n_times("s", 4, 0.2)
    user.press("enter")

    # taking the display menu screenshots
    result = find_word("aspect", interval=1, timeout=5)
    if not result:
        logging.info("Did not see aspect ratio setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video1.png")
    press_n_times("s", 14, 0.2)

    result = find_word("safezone", interval=1, timeout=5)
    if not result:
        logging.info("Did not see safezone scale setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video2.png")
    press_n_times("s", 7, 0.2)

    result = find_word("gore", interval=1, timeout=5)
    if not result:
        logging.info("Did not see gore setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video3.png")

    # navigating to the graphics menu
    user.press("backspace")
    result = find_word("graphics", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see options menu (looking for graphics). Did something mess up?"
        )
        sys.exit(1)
    user.press("s")
    user.press("enter")

    # taking the graphics screenshots
    result = find_word("preset", interval=1, timeout=5)
    if not result:
        logging.info("Did not see graphics preset setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics1.png")
    press_n_times("s", 10, 0.2)

    result = find_word("sampling", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see texture sampling quality setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics2.png")
    press_n_times("s", 7, 0.2)

    result = find_word("point", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see point lights shadow resolution setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics3.png")
    press_n_times("s", 8, 0.2)

    result = find_word("tracing", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see screen space cone tracing setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics4.png")
    press_n_times("s", 7, 0.2)

    result = find_word("scattering", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see screen space sub-surface scattering setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics5.png")
    press_n_times("s", 6, 0.2)

    result = find_word("bloom", interval=1, timeout=5)
    if not result:
        logging.info("Did not see bloom resolution setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics6.png")
    press_n_times("s", 6, 0.2)

    result = find_word("ambient", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see ambient character density setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics7.png")
    time.sleep(0.5)

    # navigating back to main menu
    press_n_times("backspace", 2, 0.2)

    result = find_word("behind", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not see main menu after taking the graphics screenshots. Did something mess up?"
        )
        sys.exit(1)


def navigate_main_menu() -> None:
    """Input to navigate main menu"""
    logging.info("Navigating main menu")

    # Enter TLOU menu
    time.sleep(5)
    user.press("space")
    time.sleep(0.5)
    take_screenshots()

    # Copy the autosave here
    copy_autosave()
    time.sleep(5)

    # navigating to the load menu
    press_n_times("w", 2, 0.2)
    user.press("space")
    time.sleep(0.5)

    result = find_word("load", interval=1, timeout=5)
    if not result:
        logging.info("Did not see story menu. Did something mess up?")
        sys.exit(1)

    # Press load game
    press_n_times("s", 2, 0.2)
    user.press("space")
    time.sleep(0.5)

    # Verify in the load section
    result = find_word("hometown", interval=1, timeout=5)
    if not result:
        logging.info(
            "Did not saves to load. Did something mess up? Or did you forget to delete the saves?"
        )
        sys.exit(1)

    # load the save
    user.press("space")
    time.sleep(0.5)


def run_benchmark():
    """Starts the benchmark"""
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    time.sleep(30)

    result = find_word("press", interval=5, timeout=120)
    if not result:
        logging.info("Did not see start screen")
        sys.exit(1)

    # copy_autosave()

    navigate_main_menu()

    # press load save
    result = find_word("yes", timeout=10, interval=1)
    if not result:
        logging.info("Did not load the save")
        sys.exit(1)

    user.press("a")
    time.sleep(0.5)
    user.press("space")

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = find_word("tommy", interval=0.2, timeout=250)
    if not result:
        logging.info("Did not see Tommy's first subtitle. Did the game load?")
        sys.exit(1)
    test_start_time = int(time.time())
    logging.info("Saw Tommy's first line. Benchmark has started.")

    # wait for black screen
    time.sleep(150)

    # This actually looks for "from?" but the current ML model sees it as fromy
    result = find_word("from", interval=0.2, timeout=250)
    if not result:
        logging.info("Did not find prompt to end harness.")
        sys.exit(1)

    # Wait for black screen
    time.sleep(24)

    test_end_time = int(time.time())

    time.sleep(2)
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)

    terminate_process(PROCESS_NAME)

    logging.info("Sleeping to let steam cloud catch up as to avoid overriding.")
    time.sleep(10)

    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    steam_id = get_active_steam_account_id()
    config_path = (
        Path(os.environ["USERPROFILE"])
        / "Saved Games"
        / "The Last of Us Part I"
        / "users"
        / str(steam_id)
        / "screeninfo.cfg"
    )
    height, width = get_resolution(str(config_path))
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }
    write_report_json(LOG_DIRECTORY, "report.json", report)

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
