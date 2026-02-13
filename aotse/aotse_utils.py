"""Utility functions for Ashes of the Singularity: Escalation test script"""
import os
import re
import sys
import logging
import getpass
from pathlib import Path
import psutil
import glob
import time
import shutil
from argparse import ArgumentParser

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.steam import get_app_install_location

USERNAME = getpass.getuser()
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
STEAM_GAME_ID = 507490
CONFIG_FILENAME = "settings.ini"
USERNAME = getpass.getuser()
CONFIG_PATH = Path(f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Ashes of the Singularity - Escalation")
EXE_PATH = Path(get_app_install_location(STEAM_GAME_ID))
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

def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    parser.add_argument(
        "--benchmark", dest="benchmark", help="Benchmark test type", required=True, choices=BENCHMARK_CONFIG.keys())
    return parser.parse_args()

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
    for thefile in files:
        try:
            os.remove(thefile)
            logging.info("Deleted old score file: %s", thefile)
        except Exception as e:
            print(f"Error deleting file {thefile}: {e}")

def find_score_in_log(score_name, file):
    """Reads score from local game log"""
    files = sorted(glob.glob(os.path.join(CONFIG_PATH, file)), key=os.path.getmtime, reverse=True)
    if not files:
        return None

    score_pattern = re.compile(rf"^{score_name}\s*(\d+\.\d+) FPS")
    score_value = 0
    with open(files[0], encoding="ANSI") as thefile:
        lines = thefile.readlines()
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
    logging.info("Waiting for benchmark process '%s' to start...", process_name)

    start_time = time.time()

    while True:
        # Check if the benchmark process is running
        process = is_process_running(process_name)
        if process:
            logging.info("%s has started. Waiting for it to finish...", test_name)
            process.wait()  # This will block until the process finishes
            logging.info("Benchmark has finished.")
            break

        # If we exceed the timeout, break out of the loop and log an error
        if time.time() - start_time > timeout:
            logging.error("Timeout reached while waiting for process '%s'.", process_name)
            raise TimeoutError(f"Process '{process_name}' did not start within the expected time. Is the game configured for DX12?")

        # Wait for 1 second before checking again
        time.sleep(1)

def replace_exe():
    """Replaces the Strange Brigade launcher exe with the Vulkan exe for immediate launching
    """
    check_backup = Path(f"{EXE_PATH}\\StardockLauncher_launcher.exe")
    launcher_exe = Path(f"{EXE_PATH}\\StardockLauncher.exe")
    dx12_exe = Path(f"{EXE_PATH}\\AshesEscalation_DX12.exe")
    if not os.path.exists(check_backup):
        os.rename(launcher_exe, check_backup)
        shutil.copy(dx12_exe, launcher_exe)
        logging.info("Replacing launcher file in %s", EXE_PATH)
    elif os.path.exists(check_backup):
        if not os.path.exists(launcher_exe):
            shutil.copy(dx12_exe, launcher_exe)
            logging.info("Replacing launcher file in %s", EXE_PATH)
        else:
            logging.info("Launcher already replaced with DX12 exe.")

def restore_exe():
    """Restores the launcher exe back to the original exe name to close the loop.
    """
    check_backup = Path(f"{EXE_PATH}\\StardockLauncher_launcher.exe")
    launcher_exe = Path(f"{EXE_PATH}\\StardockLauncher.exe")
    if not os.path.exists(check_backup):
        logging.info("Launcher already restored or file does not exist.")
    elif os.path.exists(check_backup):
        if not os.path.exists(launcher_exe):
            os.rename(check_backup, launcher_exe)
            logging.info("Restoring launcher file in %s", EXE_PATH)
        else:
            os.remove(launcher_exe)
            os.rename(check_backup, launcher_exe)
            logging.info("Restoring launcher file in %s", EXE_PATH)
