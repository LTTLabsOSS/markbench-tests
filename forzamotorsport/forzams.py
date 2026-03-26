"""Forza Motorsport test script."""

import logging
import os
import sys
import time
from pathlib import Path

from forzams_utils import get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.rtss import copy_rtss_profile, start_rtss_process
from harness_utils.steam import exec_steam_run_command, get_build_id

STEAM_GAME_ID = 2440510
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
LOCAL_USER_SETTINGS = (
    Path(os.getenv("LOCALAPPDATA"))
    / "Microsoft.ForzaMotorsport"
    / "User_SteamLocalStorageDirectory"
    / "ConnectedStorage"
    / "ForzaUserConfigSelections"
    / "UserConfigSelections"
)
PROCESSES = ["forza_steamworks_release_final.exe", "RTSS.exe"]


def launch_game() -> None:
    """Handle pre-launch setup and game launch."""
    profile_path = SCRIPT_DIRECTORY / "forza_steamworks_release_final.exe.cfg"
    copy_rtss_profile(str(profile_path))
    start_rtss_process()
    time.sleep(10)
    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(50)

    if not find_word("play", timeout=30, interval=1, msg="Could not find the main menu. Did the game load?"):
        return FAILED_RUN

    press("f")
    time.sleep(1)

    if not find_word(
        "contrast",
        timeout=30,
        interval=1,
        msg="Did not find the accessibility settings menu. Did the menu get stuck?",
    ):
        return FAILED_RUN

    press("]*3")
    if not find_word(
        "resolution",
        timeout=30,
        interval=1,
        msg="Did not find the display settings menu. Did the menu get stuck?",
    ):
        return FAILED_RUN
    am.take_screenshot("01_display.png", ArtifactType.CONFIG_IMAGE)

    press("]")
    if not find_word(
        "filtering",
        timeout=30,
        interval=1,
        msg="Did not find the graphics settings menu. Did the menu get stuck?",
    ):
        return FAILED_RUN
    am.take_screenshot("02_graphics_1.png", ArtifactType.CONFIG_IMAGE)

    press("down*15")
    if not find_word(
        "particle",
        timeout=30,
        interval=1,
        msg="Did not find the particle effect settings. Did the menu get stuck?",
    ):
        return FAILED_RUN
    am.take_screenshot("03_graphics_2.png", ArtifactType.CONFIG_IMAGE)

    press("down*3, up, down")
    if not find_word(
        "flare",
        timeout=30,
        interval=1,
        msg="Did not find the lens flare settings. Did the menu get stuck?",
    ):
        return FAILED_RUN
    am.take_screenshot("04_graphics_3.png", ArtifactType.CONFIG_IMAGE)

    press("[, enter")
    logging.info("Setup took %s seconds", round(int(time.time()) - setup_start_time, 2))
    time.sleep(15)

    if not find_word("results", timeout=60, interval=0.5, msg="Did not find the results screen. Did the game load?"):
        return FAILED_RUN
    am.take_screenshot("05_results.png", ArtifactType.RESULTS_IMAGE)
    test_start_time = int(time.time())
    time.sleep(180)

    if not find_word(
        "results",
        timeout=15,
        interval=0.5,
        msg="Did not find the results screen. Did the game crash during the run?",
    ):
        return FAILED_RUN

    test_end_time = int(time.time())
    time.sleep(2)
    am.copy_file(LOCAL_USER_SETTINGS, ArtifactType.CONFIG_TEXT, "config file")
    logging.info("Benchmark took %s seconds", round(test_end_time - test_start_time, 2))
    return test_start_time, test_end_time


def main() -> None:
    """Run the Forza Motorsport benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            resolution = get_resolution(str(LOCAL_USER_SETTINGS))
            report = {
                "resolution": f"{resolution}",
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
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
