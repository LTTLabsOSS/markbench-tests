"""F1 24 test script"""

import logging
import os.path
import re
import sys
import time
from pathlib import Path

from f1_24_utils import get_resolution

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
    get_app_install_location,
    get_build_id,
)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "F1_24"
STEAM_GAME_ID = 2488620
VIDEO_PATH = Path(get_app_install_location(STEAM_GAME_ID)) / "videos"

username = os.getlogin()
CONFIG_PATH = f"C:\\Users\\{username}\\Documents\\My Games\\F1 24\\hardwaresettings"
CONFIG_FILENAME = "hardware_settings_config.xml"
CONFIG = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"
BENCHMARK_RESULTS_PATH = f"C:\\Users\\{username}\\Documents\\My Games\\F1 24\\benchmark"

intro_videos = [VIDEO_PATH / "attract.bk2", VIDEO_PATH / "cm_f1_sting.bk2"]


def find_latest_result_file(base_path):
    """Look for files in the benchmark results path that match the pattern in the regular expression"""
    pattern = r"benchmark_.*\.xml"
    result_files = [
        path
        for path in Path(base_path).iterdir()
        if path.is_file() and re.search(pattern, path.name, re.IGNORECASE)
    ]
    return max(result_files, key=lambda path: path.stat().st_mtime)


def launch_game() -> None:
    """Handle pre-game setup and launch F1 24."""
    remove_files([str(path) for path in intro_videos])
    exec_steam_run_command(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Runs the actual benchmark."""
    launch_game()
    time.sleep(2)

    if not find_word(
        "product",
        timeout=80,
    ):
        return FAILED_RUN

    press("space*3")
    time.sleep(4)

    if not find_word(
        "press",
        interval=2,
        timeout=80,
    ):
        return FAILED_RUN

    logging.info("Hit the title screen. Continuing")
    press("enter")
    time.sleep(1)

    if find_word("login", timeout=50):
        logging.info("Cancelling logging in.")
        press("enter")
        time.sleep(2)

    if find_word("signed", timeout=50):
        press("enter")

    if not find_word(
        "theatre",
        interval=3,
        timeout=60,
    ):
        return FAILED_RUN

    logging.info("Saw the options! we are good to go!")
    time.sleep(1)

    press("down*6, enter")
    time.sleep(2)

    if not find_word(
        "graphics",
        timeout=15,
        interval=3,
    ):
        return FAILED_RUN
    press("right, enter")
    time.sleep(1.5)

    press("down*3, enter")

    if not find_word(
        "vsync",
        interval=3,
        timeout=60,
    ):
        return FAILED_RUN
    press("down*18")

    am.take_screenshot("01_video.png", ArtifactType.CONFIG_IMAGE)
    press("esc")

    if not find_word(
        "steering",
        interval=3,
        timeout=60,
    ):
        return FAILED_RUN

    am.take_screenshot("02_graphics_1.png", ArtifactType.CONFIG_IMAGE)
    press("down*29")

    if not find_word(
        "chromatic",
        interval=3,
        timeout=60,
    ):
        return FAILED_RUN

    am.take_screenshot("03_graphics_2.png", ArtifactType.CONFIG_IMAGE)
    press("up*28, enter")

    # Navigate benchmark menu
    if not find_word(
        "weather",
        timeout=15,
        interval=3,
        msg="Didn't find weather!",
    ):
        return FAILED_RUN

    am.take_screenshot("04_benchmark.png", ArtifactType.CONFIG_IMAGE)

    press("down*6, enter")
    time.sleep(2)

    if not find_word(
        "lap",
        timeout=90,
        msg="Benchmark didn't start.",
    ):
        return FAILED_RUN

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    test_start_time = int(time.time()) + 8

    # sleep for 3 laps
    time.sleep(310)

    test_end_time = None

    result = find_word("loading", timeout=90)
    if result:
        logging.info("Found the loading screen. Marking the out time.")
        test_end_time = int(time.time()) - 2
        time.sleep(2)
    else:
        logging.info("Could not find the loading screen. Could not mark end time!")

    if not find_word(
        "results",
        interval=3,
        timeout=90,
    ):
        return FAILED_RUN
    logging.info("Results screen was found! Finishing benchmark.")
    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)
    am.take_screenshot("05_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(CONFIG, ArtifactType.CONFIG_TEXT, "config file")
    am.copy_file(results_file, ArtifactType.RESULTS_TEXT, "benchmark results xml file")

    if test_end_time is None:
        logging.info(
            "Loading screen end time not found. Using results screen fallback time."
        )
        test_end_time = int(time.time())

    return test_start_time, test_end_time


def main() -> None:
    """Run the F1 24 benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            width, height = get_resolution()
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
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)
        terminate_processes(PROCESS_NAME)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
