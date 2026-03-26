"""Doom: The Dark Ages test script."""

import logging
import os.path
import sys
import time
from pathlib import Path

from doomdarkages_utils import copy_launcher_config, get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.misc import mouse_scroll_n_times
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "DOOMTheDarkAges"
STEAM_GAME_ID = 3017860
username = os.getlogin()
BENCHMARK_RESULTS_PATH = (
    f"C:\\Users\\{username}\\Saved Games\\id Software\\DOOMTheDarkAges\\base\\benchmark"
)


def launch_game() -> None:
    copy_launcher_config()
    exec_steam_game(STEAM_GAME_ID, game_params=["+com_skipIntroVideo", "1"])


def find_latest_result_file(base_path):
    base_path = Path(base_path)
    files = list(base_path.glob("benchmark-*.json"))
    if not files:
        raise ValueError(f"No benchmark-*.json files found in {base_path}")
    return max(files, key=lambda p: p.stat().st_mtime)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run the actual benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(25)

    if not find_word("press", vulkan=True, timeout=80, msg="Didn't see title screen. Check settings and try again."):
        return FAILED_RUN
    time.sleep(2)
    press("space")
    time.sleep(4)

    if not find_word("campaign", vulkan=True, interval=3, timeout=60, msg="Didn't land on the main menu!"):
        return FAILED_RUN

    press("down*3, enter")
    time.sleep(1)
    if not find_word("daze", vulkan=True, interval=3, timeout=15, msg="Didn't see the game settings. Did it navigate correctly?"):
        return FAILED_RUN
    press("q*2")
    time.sleep(1)

    if not find_word("display", vulkan=True, interval=3, timeout=15, msg="Didn't find the video settings. Did it navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("01_video_1.png", ArtifactType.CONFIG_IMAGE)
    mouse_scroll_n_times(6, -200, 0.2)
    time.sleep(1)

    if not find_word("nvidia", vulkan=True, interval=3, timeout=15, msg="Didn't find the NVIDIA Reflex setting. Did it navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("02_video_2.png", ArtifactType.CONFIG_IMAGE)
    mouse_scroll_n_times(6, -200, 0.2)
    time.sleep(1)

    if not find_word("advanced", vulkan=True, interval=3, timeout=15, msg="Didn't find the advanced heading. Did it navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("03_video_3.png", ArtifactType.CONFIG_IMAGE)
    mouse_scroll_n_times(5, -200, 0.2)
    time.sleep(1)

    if not find_word("shading", vulkan=True, interval=3, timeout=15, msg="Didn't find the shading quality setting. Did it navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("04_video_4.png", ArtifactType.CONFIG_IMAGE)
    mouse_scroll_n_times(5, -220, 0.2)
    time.sleep(0.2)

    if not find_word("brightness", vulkan=True, interval=3, timeout=15, msg="Didn't find the brightness setting. Did it navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("05_video_5.png", ArtifactType.CONFIG_IMAGE)
    press("escape")

    if not find_word("campaign", vulkan=True, interval=3, timeout=20, msg="Didn't land on the main menu!"):
        return FAILED_RUN

    press("up, enter")
    time.sleep(1)
    if not find_word("benchmarks", vulkan=True, interval=3, timeout=15, msg="Didn't navigate to the extras menu. Did it navigate properly?"):
        return FAILED_RUN

    press("up, enter")
    time.sleep(1)
    if not find_word("abyssal", vulkan=True, interval=3, timeout=15, msg="Don't see the Abyssal Forest benchmark option. Did it navigate properly?"):
        return FAILED_RUN

    press("down*2, enter")
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("frame", vulkan=True, interval=0.5, timeout=90, msg="Benchmark didn't start. Did the game crash?"):
        return FAILED_RUN

    test_start_time = int(time.time()) + 8
    time.sleep(110)

    if not find_word("results", vulkan=True, interval=0.5, timeout=90, msg="Results screen was not found!Did harness not wait long enough? Or test was too long?"):
        return FAILED_RUN

    test_end_time = int(time.time()) - 2
    time.sleep(2)
    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)
    am.take_screenshot_vulkan("06_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(results_file, ArtifactType.RESULTS_TEXT, "benchmark results/settings xml file")
    logging.info("Benchmark took %f seconds", round(test_end_time - test_start_time, 2))
    return test_start_time, test_end_time


def main() -> None:
    """Run the DOOM: The Dark Ages benchmark harness."""
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
        terminate_processes(PROCESS_NAME)
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
