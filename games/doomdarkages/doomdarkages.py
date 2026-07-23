"""Doom: The Dark Ages test script"""

import logging
import sys
import time
from pathlib import Path

from doomdarkages_utils import get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from doomdarkages_utils import copy_launcher_config

from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact, reset_artifacts
from harness_utils.input import (
    mangohud_log_toggle,
    mouse_scroll_n_times,
    press_n_times,
    user,
)
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, user_saved_games
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "DOOMTheDarkAges.exe"
STEAM_GAME_ID = 3017860
BENCHMARK_RESULTS_PATH = (
    user_saved_games(STEAM_GAME_ID)
    / "id Software"
    / "DOOMTheDarkAges"
    / "base"
    / "benchmark"
)

user.FAILSAFE = False


def start_game():
    """Launch the game with no launcher or start screen"""
    copy_launcher_config()
    return exec_steam_game(STEAM_GAME_ID, game_params=["+com_skipIntroVideo", "1"])


def find_latest_result_file(base_path):
    """Look for files in the benchmark results path that match the pattern.
    Returns the most recent benchmark file."""
    base_path = Path(base_path)

    files = list(base_path.glob("benchmark-*.json"))
    if not files:
        raise ValueError(f"No benchmark-*.json files found in {base_path}")

    return max(files, key=lambda p: p.stat().st_mtime)


def run_benchmark():
    """Runs the actual benchmark."""
    start_game()
    reset_artifacts(ARTIFACTS_DIRECTORY)

    setup_start_time = int(time.time())
    time.sleep(25)
    # Press space to proceed to the main menu
    result = find_word("press", vulkan=True, timeout=80)
    if not result:
        logging.info("Didn't see title screen. Check settings and try again.")
        sys.exit(1)

    if is_linux():
        mangohud_log_toggle()

    logging.info("Hit the title screen. Continuing")
    time.sleep(2)
    user.press("space")
    time.sleep(4)

    # Navigate menus and take screenshots using the artifact manager
    result = find_word("campaign", vulkan=True, interval=3, timeout=60)
    if not result:
        logging.info("Didn't land on the main menu!")
        sys.exit(1)

    logging.info("Saw the main menu. Proceeding.")
    time.sleep(1)

    press_n_times("down", 4, 0.5)
    user.press("enter")
    time.sleep(1)

    result = find_word("daze", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info("Didn't see the game settings. Did it navigate correctly?")
        sys.exit(1)

    logging.info("Saw the game settings. Proceeding.")
    press_n_times("q", 2, 0.5)
    time.sleep(1)

    # Screenshotting the display settings
    result = find_word("display", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the video settings. Did it navigate correctly?")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video1.png", vulkan=True)
    mouse_scroll_n_times(7, -120, 0.5)
    time.sleep(1)

    result = find_word("fsr", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info(
            "Didn't find the FSR setting. Did it navigate correctly?"
        )
        sys.exit(1)

<<<<<<< HEAD
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video2.png", vulkan=True)
    mouse_scroll_n_times(6, -120, 0.5)
>>>>>>> 2f4b1da (Move more game artifacts)
    time.sleep(1)

    result = find_word("tracing", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the path tracing heading. Did it navigate correctly?")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video3.png", vulkan=True)
    mouse_scroll_n_times(5, -120, 0.5)
    time.sleep(1)

    result = find_word("decal", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info(
            "Didn't find the decal quality setting. Did it navigate correctly?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video4.png", vulkan=True)
    mouse_scroll_n_times(5, -120, 0.5)
    time.sleep(0.5)

    result = find_word("brightness", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the brightness setting. Did it navigate correctly?")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video5.png", vulkan=True)
    user.press("escape")
    time.sleep(0.5)

    # Navigating to the benchmark
    result = find_word("campaign", vulkan=True, interval=3, timeout=20)
    if not result:
        logging.info("Didn't land on the main menu!")
        sys.exit(1)

    logging.info("Saw the main menu. Proceeding.")
    time.sleep(1)

    user.press("up")
    user.press("enter")
    time.sleep(1)

    result = find_word("benchmarks", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info("Didn't navigate to the extras menu. Did it navigate properly?")
        sys.exit(1)

    logging.info("Saw the extras menu. Proceeding.")
    time.sleep(1)

    user.press("up")
    user.press("enter")
    time.sleep(1)

    result = find_word("abyssal", vulkan=True, interval=3, timeout=15)
    if not result:
        logging.info(
            "Don't see the Abyssal Forest benchmark option. Did it navigate properly?"
        )
        sys.exit(1)

    logging.info("See the benchmarks. Starting the Abyssal Forest benchmark level.")
    time.sleep(1)

    press_n_times("down", 2, 0.5)
    user.press("enter")
    time.sleep(1)

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = find_word("frame", vulkan=True, interval=0.5, timeout=90)
    if not result:
        logging.info("Benchmark didn't start. Did the game crash?")
        sys.exit(1)

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    test_start_time = int(time.time()) + 8

    # Sleeping for the duration of the benchmark
    time.sleep(110)

    test_end_time = None

    result = find_word("results", vulkan=True, interval=0.5, timeout=90)
    if result:
        logging.info("Found the results screen. Marking the out time.")
        test_end_time = int(time.time()) - 2
        time.sleep(2)
    else:
        logging.info(
            "Results screen was not found!"
            + "Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    logging.info("Results screen was found! Finishing benchmark.")
    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png", vulkan=True)
    copy_artifact(results_file, ARTIFACTS_DIRECTORY)

    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    if is_linux():
        mangohud_log_toggle()

    terminate_process(PROCESS_NAME)


    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
