"""tiny tinas wonderlands test script"""
from pathlib import Path
import time
import pydirectinput as user
import logging
import sys
import os
from utils import read_resolution, get_documents_path, find_latest_result_file
from argparse import ArgumentParser

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    format_resolution, seconds_to_milliseconds, setup_log_directory, write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY.joinpath("run")
STEAM_GAME_ID = 1286680
EXECUTABLE = "Wonderlands.exe"

def setup_logging():
    """default logging config"""
    setup_log_directory(LOG_DIRECTORY)
    logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def start_game() -> any:
    """start the game"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-nostartupmovies"])


def run_benchmark():
    """run benchmark"""
    start_game()

    t1 = int(time.time())
    optimizing_shaders = kerasService.look_for_word("optimize", interval=1, attempts=10)
    if optimizing_shaders:
        time.sleep(40)

    # wait for menu to load
    time.sleep(20)

    options_present = kerasService.wait_for_word("options", interval=1, timeout=60)
    if options_present is None:
        raise ValueError("game did not load within time")

    logging.info('Saw the options! we are good to go!')
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(4)

    visuals = kerasService.wait_for_word("visuals", interval=1, timeout=10)
    if visuals is None:
        raise ValueError("on the wrong menu!")

    am.take_screenshot("graphics_1.png", ArtifactType.CONFIG_IMAGE, "first screenshot of graphics settings")

    user.press("altleft")
    time.sleep(0.5)

    am.take_screenshot("graphics_2.png", ArtifactType.CONFIG_IMAGE, "second screenshot of graphics settings")
    time.sleep(1)

    for _ in range(18):
        user.press("down")
        time.sleep(0.5)

    am.take_screenshot("graphics_3.png", ArtifactType.CONFIG_IMAGE, "third screenshot of graphics settings")

    user.press("altleft")
    time.sleep(0.5)

    benchmark = kerasService.wait_for_word("benchmark", interval=1, timeout=10)
    if benchmark is None:
        raise ValueError("could not find benchmark button")

    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1)


    t2 = int(time.time())
    duration =  round((t2 - t1), 2)
    logging.info("Harness setup took %d seconds", duration)

    result = kerasService.wait_for_word("fps", interval=0.5, timeout=30)
    if result is None:
        raise ValueError("benchmark didn't start on time or at all")

    benchmark_start = int(time.time())
    time.sleep(110)
    result = kerasService.wait_for_word("options", interval=0.5, timeout=30)
    if result is None:
        raise ValueError("did not detect end of benchmark, should have landed back in main menu")

    benchmark_end = int(time.time())
    duration =  round((benchmark_end - benchmark_start), 2)
    logging.info("Benchmark took %d seconds", duration)
    terminate_processes("Wonderlands")
    return benchmark_start, benchmark_end


try:
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    kerasService = KerasService(args.keras_host, args.keras_port)
    am = ArtifactManager(LOG_DIRECTORY)
    start_time, end_time = run_benchmark()
    height, width = read_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID)
    }

    my_documents_path = get_documents_path()
    settings_path = Path(my_documents_path, r"My Games\Tiny Tina's Wonderlands\Saved\Config\WindowsNoEditor\GameUserSettings.ini")
    am.copy_file(settings_path, ArtifactType.CONFIG_TEXT, "settings file")
    saved_results_dir = Path(my_documents_path, r"My Games\Tiny Tina's Wonderlands\Saved\BenchmarkData")
    benchmark_results = find_latest_result_file(str(saved_results_dir))
    am.copy_file(benchmark_results, ArtifactType.RESULTS_TEXT, "results file")

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes("Wonderlands")
    sys.exit(1)
