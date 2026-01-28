"""F1 24 test script"""

import os.path
import re
import sys
import time
from pathlib import Path

from f1_24_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, int_time, press
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

f1_folder = Path.home() / "Documents" / "My Games" / "F1 24"
CONFIG_PATH = f1_folder / "hardwaresettings"
CONFIG = CONFIG_PATH / "hardware_settings_config.xml"
BENCHMARK_RESULTS_PATH = f1_folder / "benchmark"

intro_videos = [
    os.path.join(VIDEO_PATH, "attract.bk2"),
    os.path.join(VIDEO_PATH, "cm_f1_sting.bk2"),
]




def find_latest_result_file(base_path):
    pattern = r"benchmark_.*\.xml"
    directory = Path(base_path)

    list_of_files = [
        p for p in directory.iterdir() if re.search(pattern, p.name, re.IGNORECASE)
    ]

    latest_file = max(list_of_files, key=lambda p: p.stat().st_mtime)

    return latest_file


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    # navigating settings
    if not find_word("product", timeout=60):
        return (0, 0)

    press("space*3", pause=1)

    if not find_word("press", timeout=30):
        return (0, 0)

    press("enter")

    if not find_word("login", timeout=30):
        return (0, 0)

    press("enter")

    if not find_word("signed", timeout=30):
        return (0, 0)

    press("enter")

    if not find_word("theatre", "Did not find theatre on main menu", timeout=60):
        return (0, 0)

    press("down*6,enter")

    if not find_word("graphics"):
        return (0, 0)

    press("right, enter")

    # check if in graphics here

    press("down*3,enter")

    if not find_word("vsync", "vsync in video menu not found"):
        return (0, 0)
    press("down*18")

    am.take_screenshot("1_video.png", ArtifactType.CONFIG_IMAGE, "video setting")

    press("esc")

    if not find_word("steering", "sterring not found after leaving video menue"):
        return (0, 0)

    am.take_screenshot(
        "2_graphics1.png", ArtifactType.CONFIG_IMAGE, "graphics settings 1"
    )
    press("down*29")

    if not find_word("chromatic"):
        return (0, 0)

    am.take_screenshot(
        "3_graphics2.png", ArtifactType.CONFIG_IMAGE, "graphics settings2 "
    )

    press("up*28,enter")

    if not find_word("weather"):
        return (0, 0)

    am.take_screenshot(
        "4_benchmark.png", ArtifactType.CONFIG_IMAGE, "benchmark settings"
    )

    press("down*6,enter")

    # looking for start in time of benchmark
    if not find_word("lap", "lap at benchmark start not seen"):
        return (0, 0)

    test_start_time = int_time() + 8

    time.sleep(310)

    test_end_time = None

    if not find_word("loading", "loading screen not found"):
        return (0, 0)

    test_end_time = int_time() - 2
    time.sleep(2)

    if not find_word("results"):
        return (0, 0)

    am.take_screenshot(
        "result.png", ArtifactType.RESULTS_IMAGE, "screenshot of results"
    )

    return test_start_time, test_end_time


def main():
    setup_logging(LOG_DIRECTORY)

    am = ArtifactManager(LOG_DIRECTORY)

    remove_files(intro_videos)

    exec_steam_run_command(STEAM_GAME_ID)

    start_time, end_time = run_benchmark(am)

    terminate_processes(PROCESS_NAME)

    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)

    am.copy_file(CONFIG, ArtifactType.CONFIG_TEXT, "config file")

    am.copy_file(results_file, ArtifactType.RESULTS_TEXT, "benchmark results xml file")

    am.create_manifest()

    width, height = get_resolution()

    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)

    sys.exit(0)


if __name__ == "__main__":
    main()
