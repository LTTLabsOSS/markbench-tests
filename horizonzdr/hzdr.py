"""Horizon Zero Dawn Remastered test script."""

import logging
import sys
import time
import winreg
from pathlib import Path

from hzdr_utils import get_resolution, process_registry_file

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.misc import remove_files
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    exec_steam_run_command,
    get_build_id,
    get_steamapps_common_path,
)

STEAM_GAME_ID = 2561580
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "HorizonZeroDawnRemastered"
VIDEO_PATH = (
    Path(get_steamapps_common_path())
    / "Horizon Zero Dawn Remastered"
    / "Movies"
    / "Mono"
)
INPUT_FILE = SCRIPT_DIRECTORY / "graphics.reg"
CONFIG_FILE = SCRIPT_DIRECTORY / "graphics_config.txt"
hive = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\\Guerrilla Games\\Horizon Zero Dawn Remastered\\Graphics"

intro_videos = [
    VIDEO_PATH / "weaseltron_logo.bk2",
    VIDEO_PATH / "sony_studios_reel.bk2",
    VIDEO_PATH / "nixxes_logo.bk2",
    VIDEO_PATH / "Logo.bk2",
    VIDEO_PATH / "guerilla_logo.bk2",
]


def launch_game() -> None:
    logging.info("Removing intro videos")
    remove_files([str(path) for path in intro_videos])
    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(10)

    if not find_word("quit", timeout=30, interval=1, msg="Could not find the main menu. Did the game load?"):
        return FAILED_RUN

    press("down*2, enter")
    if not find_word("language", timeout=30, interval=1, msg="Did not find the video settings menu. Did the menu get stuck?"):
        return FAILED_RUN

    press("e")
    if not find_word("monitor", timeout=30, interval=1, msg="Did not find the display settings menu. Did the menu get stuck?"):
        return FAILED_RUN
    am.take_screenshot("01_display_1.png", ArtifactType.CONFIG_IMAGE)

    press("up")
    if not find_word("upscale", timeout=30, interval=1, msg="Did not find the upscale settings. Did the menu not scroll?"):
        return FAILED_RUN
    am.take_screenshot("02_display_2.png", ArtifactType.CONFIG_IMAGE)

    press("e")
    if not find_word("preset", timeout=30, interval=1, msg="Did not find the graphics settings menu. Did the menu get stuck?"):
        return FAILED_RUN
    am.take_screenshot("03_graphics_1.png", ArtifactType.CONFIG_IMAGE)

    press("up")
    if not find_word("sharpness", timeout=30, interval=1, msg="Did not find the sharpness settings. Did the menu not scroll?"):
        return FAILED_RUN
    am.take_screenshot("04_graphics_2.png", ArtifactType.CONFIG_IMAGE)

    press("tab, enter")
    logging.info("Setup took %s seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("continue", timeout=120, interval=1, msg="Did not find the continue button. Did the game not finish loading?"):
        return FAILED_RUN

    press("enter")
    test_start_time = int(time.time())
    time.sleep(180)

    if not find_word("results", timeout=20, interval=0.1, msg="Did not find the results screen. Did the game not finish the benchmark?"):
        return FAILED_RUN

    test_end_time = int(time.time())
    time.sleep(2)
    am.take_screenshot("05_results.png", ArtifactType.RESULTS_IMAGE)
    process_registry_file(hive, SUBKEY, str(INPUT_FILE), str(CONFIG_FILE))
    am.copy_file(CONFIG_FILE, ArtifactType.CONFIG_TEXT, "config file")
    logging.info("Benchmark took %s seconds", round(test_end_time - test_start_time, 2))
    time.sleep(15)
    return test_start_time, test_end_time


def main() -> None:
    """Run the Horizon Zero Dawn Remastered benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = get_resolution(str(CONFIG_FILE))
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
            }
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
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
