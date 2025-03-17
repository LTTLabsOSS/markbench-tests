"""Ashes of the Singularity: Escalation test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import subprocess
import sys
import time
import getpass
import glob
import os
from aotse_utils import read_current_resolution, find_score_in_log, wait_for_benchmark_process, delete_old_scores, get_args

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.keras_service import KerasService
from harness_utils.steam import get_app_install_location, get_build_id, exec_steam_game
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    format_resolution,
    write_report_json
)
from harness_utils.artifacts import ArtifactManager, ArtifactType

#####
### Globals
#####
USERNAME = getpass.getuser()
CONFIG_PATH = Path(f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Ashes of the Singularity - Escalation")
CONFIG_FILENAME = "settings.ini"
STEAM_GAME_ID = 507490
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
EXECUTABLE = "AshesEscalation_DX12.exe"
CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "GPU_Benchmark": {
        "hardware": "GPU",
        "config": "benchfinal",
        "score_name": "Avg Framerate:",
        "test_name": "Ashes of the Singularity: Escalation GPU Benchmark"
    },
    "CPU_Benchmark": {
        "hardware": "CPU",
        "config": "CPUbench",
        "score_name": r"CPU frame rate \(estimated if not GPU bound\):",
        "test_name": "Ashes of the Singularity: Escalation CPU Benchmark"
    }
}
CFG = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"
GAME_DIR = get_app_install_location(STEAM_GAME_ID)

def start_game():
    """Launch the game with no launcher or start screen"""
    test_option = BENCHMARK_CONFIG[args.benchmark]["config"]
    return exec_steam_game(STEAM_GAME_ID, game_params=["-benchmark", f"{test_option}"])

def run_benchmark():
    """Start the benchmark"""
     # Start game via Steam and enter fullscreen mode
    setup_start_time = time.time()
    start_game()

    time.sleep(10)

    result = kerasService.wait_for_word("preparing", interval=3, timeout=60)
    if not result:
        logging.info("Did not see the benchmark starting.")
        sys.exit(1)

    # Start the benchmark!
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    time.sleep(15)

    result = kerasService.wait_for_word("259", timeout=60, interval=0.2)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    test_start_time = time.time()

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(180)
    # result = kerasService.wait_for_word("complete", timeout=240, interval=0.5)
    # if not result:
    #     logging.info("Did not see the Benchmark Complete pop up. Did it run?")
    #     sys.exit(1)

    test_end_time = time.time() - 2
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)
    return test_start_time, test_end_time

setup_log_directory(LOG_DIR)
logging.basicConfig(filename=LOG_DIR / "harness.log",
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

args = get_args()
kerasService = KerasService(args.keras_host, args.keras_port)
am = ArtifactManager(LOG_DIR)

try:
    logging.info('Starting benchmark!')
    RESULT="Output_*_*_*_*.txt"
    delete_old_scores(RESULT)
    start_time, end_time = run_benchmark()
    score = find_score_in_log(BENCHMARK_CONFIG[args.benchmark]["score_name"], RESULT)

    if score is None:
        logging.error("Could not find average FPS output!")
        sys.exit(1)
    logging.info("Score was %s", score)

    am.copy_file(CFG, ArtifactType.CONFIG_TEXT, "Settings file")
    result_file = sorted(glob.glob(os.path.join(CONFIG_PATH, RESULT)), key=os.path.getmtime, reverse=True)
    output_file = result_file[0]
    am.copy_file(output_file, ArtifactType.CONFIG_TEXT, "Results file")
    hardware = BENCHMARK_CONFIG[args.benchmark]["hardware"]
    width, height = read_current_resolution()
    report = {
        "test": BENCHMARK_CONFIG[args.benchmark]["test_name"],
        "unit": f"Average {hardware} FPS",
        "score": score,
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID)
    }

    am.create_manifest()
    write_report_json(LOG_DIR, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
