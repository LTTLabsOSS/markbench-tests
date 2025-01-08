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
from aotse_utils import read_current_resolution, find_score_in_log, wait_for_benchmark_process, delete_old_scores

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.steam import get_app_install_location, get_build_id
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
        "score_name": "CPU frame rate \(estimated if not GPU bound\):",
        "test_name": "Ashes of the Singularity: Escalation CPU Benchmark"
    }
}
cfg = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"
GAME_DIR = get_app_install_location(STEAM_GAME_ID)


def setup_logging():
    """setup logging"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=LOG_DIR / "harness.log",
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--benchmark", dest="benchmark", help="Benchmark test type", required=True, choices=BENCHMARK_CONFIG.keys())
    argies = parser.parse_args()
    return argies

def start_game():
    """Starts the game process"""
    test_option = BENCHMARK_CONFIG[args.benchmark]["config"]
    cmd_string = f"\"{GAME_DIR}\\{EXECUTABLE}\" -benchmark {test_option}"
    logging.info(cmd_string)
    return cmd_string

def run_benchmark(process_name, command_to_run):
    """Run the benchmark and wait for the benchmark process to finish."""
    # Start Steam via subprocess.Popen
    with subprocess.Popen(command_to_run, cwd=GAME_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as proc:
        
        # Wait for the actual benchmark process to start and finish
        test_name=BENCHMARK_CONFIG[args.benchmark]["test_name"]
        wait_for_benchmark_process(test_name, process_name)
        
        # Now that the process has finished, collect the results
        stdout, stderr = proc.communicate()  # This waits for the Steam subprocess to exit (if any)

        # Log any output and error from the Steam process
        if stdout:
            logging.info(f"Steam Output: {stdout}")
        if stderr:
            logging.error(f"Steam Error: {stderr}")
        
        # Now, return the process object
        return proc

am = ArtifactManager(LOG_DIR)

try:
    setup_logging()
    args = get_arguments()
    cmd = start_game()
    logging.info('Starting benchmark!')
    logging.info(cmd)
    start_time = time.time()
    result="Output_*_*_*_*.txt"
    delete_old_scores(result)
    run_benchmark(EXECUTABLE, cmd)
    score = find_score_in_log(BENCHMARK_CONFIG[args.benchmark]["score_name"], result)
    
    if score is None:
        logging.error("Could not find average FPS output!")
        sys.exit(1)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)
    logging.info("Score was %s", score)

    am.copy_file(cfg, ArtifactType.CONFIG_TEXT, "Settings file")
    result_file = sorted(glob.glob(os.path.join(CONFIG_PATH, result)), key=os.path.getmtime, reverse=True)
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
