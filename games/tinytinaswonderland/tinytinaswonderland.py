"""tiny tinas wonderlands test script"""

import logging
import re
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.input import mangohud_log_toggle, user
from harness_utils.ocr_service import find_word
from harness_utils.paths import harness_directories, user_documents
from harness_utils.process import terminate_process
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import exec_steam_game, get_build_id

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
STEAM_GAME_ID = 1286680
EXECUTABLE = "Wonderlands.exe"

user.FAILSAFE = False


def start_game():
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

    time.sleep(1)
    mangohud_log_toggle()
    time.sleep(1)

    logger.info("Saw the options! we are good to go!")
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
    logger.info("Harness setup took %d seconds", duration)

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
    logger.info("Benchmark took %d seconds", duration)
    terminate_process("Wonderlands")
    return benchmark_start, benchmark_end


try:
    start_time, end_time = run_benchmark()
    documents_path = user_documents(STEAM_GAME_ID)
    settings_path = (
        documents_path
        / "My Games"
        / "Tiny Tina's Wonderlands"
        / "Saved"
        / "Config"
        / "WindowsNoEditor"
        / "GameUserSettings.ini"
    )
    benchmark_results_directory = (
        documents_path
        / "My Games"
        / "Tiny Tina's Wonderlands"
        / "Saved"
        / "BenchmarkData"
    )
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    height = width = 0
    with settings_path.open(encoding="utf-8") as settings_file:
        for line in settings_file:
            height_match = height_pattern.match(line)
            width_match = width_pattern.match(line)
            if height_match is not None:
                height = int(height_match.group(1))
            if width_match is not None:
                width = int(width_match.group(1))
            if height > 0 and width > 0:
                break
    logger.info("Current resolution is %dx%d", width, height)

    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    copy_artifact(settings_path, ARTIFACTS_DIRECTORY)
    result_pattern = re.compile(r"BenchmarkData.*\.txt", re.IGNORECASE)
    benchmark_results = max(
        (
            path
            for path in benchmark_results_directory.iterdir()
            if result_pattern.search(path.name)
        ),
        key=lambda path: path.stat().st_mtime,
    )
    copy_artifact(benchmark_results, ARTIFACTS_DIRECTORY)

    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    terminate_process("Wonderlands")
    sys.exit(1)
