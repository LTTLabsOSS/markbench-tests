"""Utility functions for Total War: Warhammer III test script"""
import os
import re
import sys
import logging
import getpass
from pathlib import Path
import psutil
import glob
import time

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.steam import get_steam_exe_path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

USERNAME = getpass.getuser()
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "stellaris.exe"
STEAM_GAME_ID = 281990
CONFIG_FILENAME = "settings.ini"
USERNAME = getpass.getuser()
CONFIG_PATH = Path(f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Ashes of the Singularity - Escalation")

def read_current_resolution():
    """Get resolution from local game file"""
    resolution_pattern = re.compile(r"Resolution=(\d+),(\d+)")
    cfg = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"
    width = 0
    height = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                width, height = resolution_match.groups()
    return width, height

def delete_old_scores(file):
    """Deletes old score files based on a given pattern"""
    files = glob.glob(os.path.join(CONFIG_PATH, file))
    for file in files:
        try:
            os.remove(file)
            logging.info(f"Deleted old score file: {file}")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

def find_score_in_log(score_name, file):
    """Reads score from local game log"""
    files = sorted(glob.glob(os.path.join(CONFIG_PATH, file)), key=os.path.getmtime, reverse=True)
    if not files:
        return None
    
    score_pattern = re.compile(rf"^{score_name}\s*(\d+\.\d+) FPS")
    score_value = 0
    with open(files[0], encoding="ANSI") as file:
        lines = file.readlines()
        for line in lines:
            score_match = score_pattern.search(line)
            if score_match is not None:
                score_value = score_match.group(1)
                break
    return score_value

def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process
    return None

def wait_for_benchmark_process(test_name, process_name, timeout=60):
    """Wait for the benchmark game process to start and then finish."""
    logging.info(f"Waiting for benchmark process '{process_name}' to start...")

    start_time = time.time()

    while True:
        # Check if the benchmark process is running
        process = is_process_running(process_name)
        if process:
            logging.info(f"{test_name} has started. Waiting for it to finish...")
            process.wait()  # This will block until the process finishes
            logging.info(f"Benchmark has finished.")
            break

        # If we exceed the timeout, break out of the loop and log an error
        if time.time() - start_time > timeout:
            logging.error(f"Timeout reached while waiting for process '{process_name}'.")
            raise TimeoutError(f"Process '{process_name}' did not start within the expected time. Is the game configured for DX12?")

        # Wait for 1 second before checking again
        time.sleep(1)

def run_game_benchmark(game_id: int, steam_path=None, game_params=None):
    """Runs a game by providing steam executable with an array of parameters.
    The `steam_path` argument can be used to specify a specifc path to the Steam executable
    instead of relying on finding the current installation in the Window's registry.
    """
    if steam_path is None:
        steam_path = get_steam_exe_path()
    if game_params is None:
        game_params = []
    command = [steam_path, "-applaunch", str(game_id)] + game_params
    logging.info(", ".join(command))
    return command