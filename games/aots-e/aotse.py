"""Ashes of the Singularity: Escalation test script"""

import getpass
import logging
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from aotse_utils import (
    delete_old_scores,
    find_score_in_log,
    read_current_resolution,
    replace_exe,
    restore_exe,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import copy_artifact
from harness_utils.paths import harness_directories
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.steam import exec_steam_game, get_build_id

#####
### Globals
#####
USERNAME = getpass.getuser()
CONFIG_PATH = Path(
    f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Ashes of the Singularity - Escalation"
)
CONFIG_FILENAME = "settings.ini"
STEAM_GAME_ID = 507490
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
EXECUTABLE = "StardockLauncher.exe"
CONFIG_DIR = SCRIPT_DIRECTORY / "config"
BENCHMARK_CONFIG = {
    "GPU_Benchmark": {
        "hardware": "GPU",
        "config": "benchfinal",
        "score_name": "Avg Framerate:",
        "test_name": "Ashes of the Singularity: Escalation GPU Benchmark",
    },
    "CPU_Benchmark": {
        "hardware": "CPU",
        "config": "CPUbench",
        "score_name": r"CPU frame rate \(estimated if not GPU bound\):",
        "test_name": "Ashes of the Singularity: Escalation CPU Benchmark",
    },
}
CFG = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"


def start_game():
    """Launch the game with no launcher or start screen"""
    test_option = BENCHMARK_CONFIG[args.benchmark]["config"]
    return exec_steam_game(STEAM_GAME_ID, game_params=["-benchmark", f"{test_option}"])


def run_benchmark():
    """Start the benchmark"""
    # Start game via Steam and enter fullscreen mode
    setup_start_time = time.time()
    replace_exe()
    start_game()

    time.sleep(10)

    result = find_word("preparing", interval=1, timeout=60)
    if not result:
        logging.info("Did not see the benchmark starting.")
        sys.exit(1)

    # Start the benchmark!
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    time.sleep(15)

    result = find_word("59", timeout=60, interval=0.2)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    test_start_time = time.time()

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(180)

    test_end_time = time.time()
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)
    restore_exe()

    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

parser = ArgumentParser()
parser.add_argument(
        "--benchmark",
        dest="benchmark",
        help="Benchmark test type",
        required=True,
        choices=BENCHMARK_CONFIG.keys(),
    )
args, unknown = parser.parse_known_args()
try:
    logging.info("Starting benchmark!")
    RESULT = "Output_*_*_*_*.txt"
    delete_old_scores(RESULT)
    start_time, end_time = run_benchmark()
    score = find_score_in_log(BENCHMARK_CONFIG[args.benchmark]["score_name"], RESULT)

    if score is None:
        logging.error("Could not find average FPS output!")
        sys.exit(1)
    logging.info("Score was %s", score)

    copy_artifact(CFG, ARTIFACTS_DIRECTORY)
    result_file = sorted(
        CONFIG_PATH.glob(RESULT),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    output_file = result_file[0]
    copy_artifact(output_file, ARTIFACTS_DIRECTORY)
    hardware = BENCHMARK_CONFIG[args.benchmark]["hardware"]
    width, height = read_current_resolution()
    report = {
        "test": BENCHMARK_CONFIG[args.benchmark]["test_name"],
        "unit": f"Average {hardware} FPS",
        "score": score,
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }


    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
