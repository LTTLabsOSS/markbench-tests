"""tiny tinas wonderlands test script"""

import logging
import sys
import time
from pathlib import Path

import pydirectinput as user
from tinytinaswonderland_utils import (
    find_latest_result_file,
    get_documents_path,
    read_resolution,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact
from harness_utils.paths import harness_directories
from harness_utils.ocr_service import find_word
from harness_utils.report import format_resolution, seconds_to_milliseconds
from harness_utils.report_writing import write_report_json
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
STEAM_GAME_ID = 1286680
EXECUTABLE = "Wonderlands.exe"

user.FAILSAFE = False


def start_game() -> any:
    """start the game"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-nostartupmovies"])


def run_benchmark():
    """run benchmark"""
    start_game()

    t1 = int(time.time())
    optimizing_shaders = find_word("optimize", interval=1, timeout=10)
    if optimizing_shaders:
        time.sleep(40)

    # wait for menu to load
    time.sleep(20)

    options_present = find_word("options", interval=1, timeout=60)
    if options_present is None:
        raise ValueError("game did not load within time")

    logging.info("Saw the options! we are good to go!")
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(4)

    visuals = find_word("visuals", interval=1, timeout=10)
    if visuals is None:
        raise ValueError("on the wrong menu!")

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_1.png")

    user.press("altleft")
    time.sleep(0.5)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_2.png")
    time.sleep(1)

    for _ in range(18):
        user.press("down")
        time.sleep(0.5)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics_3.png")

    user.press("altleft")
    time.sleep(0.5)

    benchmark = find_word("benchmark", interval=1, timeout=10)
    if benchmark is None:
        raise ValueError("could not find benchmark button")

    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1)

    t2 = int(time.time())
    duration = round((t2 - t1), 2)
    logging.info("Harness setup took %d seconds", duration)

    result = find_word("fps", interval=0.5, timeout=30)
    if result is None:
        raise ValueError("benchmark didn't start on time or at all")

    benchmark_start = int(time.time())
    time.sleep(110)
    result = find_word("options", interval=0.5, timeout=30)
    if result is None:
        raise ValueError(
            "did not detect end of benchmark, should have landed back in main menu"
        )

    benchmark_end = int(time.time())
    duration = round((benchmark_end - benchmark_start), 2)
    logging.info("Benchmark took %d seconds", duration)
    terminate_process("Wonderlands")
    return benchmark_start, benchmark_end


try:
    start_time, end_time = run_benchmark()
    height, width = read_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    my_documents_path = get_documents_path()
    settings_path = Path(
        my_documents_path,
        r"My Games\Tiny Tina's Wonderlands\Saved\Config\WindowsNoEditor\GameUserSettings.ini",
    )
    copy_artifact(settings_path, ARTIFACTS_DIRECTORY)
    saved_results_dir = Path(
        my_documents_path, r"My Games\Tiny Tina's Wonderlands\Saved\BenchmarkData"
    )
    benchmark_results = find_latest_result_file(str(saved_results_dir))
    copy_artifact(benchmark_results, ARTIFACTS_DIRECTORY)


    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process("Wonderlands")
    sys.exit(1)
