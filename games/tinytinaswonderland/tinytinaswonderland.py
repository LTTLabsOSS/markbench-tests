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

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.ocr_service import find_word
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
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

    am.take_screenshot(
        "graphics_1.png",
        ArtifactType.CONFIG_IMAGE,
        "first screenshot of graphics settings",
    )

    user.press("altleft")
    time.sleep(0.5)

    am.take_screenshot(
        "graphics_2.png",
        ArtifactType.CONFIG_IMAGE,
        "second screenshot of graphics settings",
    )
    time.sleep(1)

    for _ in range(18):
        user.press("down")
        time.sleep(0.5)

    am.take_screenshot(
        "graphics_3.png",
        ArtifactType.CONFIG_IMAGE,
        "third screenshot of graphics settings",
    )

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
    am = ArtifactManager(LOG_DIRECTORY)
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
    am.copy_file(settings_path, ArtifactType.CONFIG_TEXT, "settings file")
    saved_results_dir = Path(
        my_documents_path, r"My Games\Tiny Tina's Wonderlands\Saved\BenchmarkData"
    )
    benchmark_results = find_latest_result_file(str(saved_results_dir))
    am.copy_file(benchmark_results, ArtifactType.RESULTS_TEXT, "results file")

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process("Wonderlands")
    sys.exit(1)
