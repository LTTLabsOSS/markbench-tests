"""Utility functions for Ashes of the Singularity: Escalation test script"""

import logging
import re
import shutil
import sys
import time
from pathlib import Path

import psutil

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)


from harness_utils.paths import user_documents
from harness_utils.steam import get_app_install_location

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
STEAM_GAME_ID = 507490
CONFIG_FILENAME = "settings.ini"
CONFIG_PATH = (
    user_documents(STEAM_GAME_ID) / "My Games" / "Ashes of the Singularity - Escalation"
)
EXE_PATH = get_app_install_location(STEAM_GAME_ID)


def read_current_resolution() -> tuple[int, int]:
    """Get resolution from local game file"""
    resolution_pattern = re.compile(r"Resolution=(\d+),(\d+)")
    cfg = CONFIG_PATH / CONFIG_FILENAME
    width = 0
    height = 0
    with cfg.open(encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                width, height = map(int, resolution_match.groups())
    return width, height


def delete_old_scores(file):
    """Deletes old score files based on a given pattern"""
    for thefile in CONFIG_PATH.glob(file):
        try:
            thefile.unlink()
            logger.info("Deleted old score file: %s", thefile)
        except Exception as e:
            print(f"Error deleting file {thefile}: {e}")


def find_score_in_log(score_name, file):
    """Reads score from local game log"""
    files = sorted(
        CONFIG_PATH.glob(file), key=lambda path: path.stat().st_mtime, reverse=True
    )
    if not files:
        return None

    score_pattern = re.compile(rf"^{score_name}\s*(\d+\.\d+) FPS".encode("ascii"))
    score_value = 0
    for line in files[0].read_bytes().splitlines():
        score_match = score_pattern.search(line)
        if score_match is not None:
            score_value = score_match.group(1).decode("ascii")
            break
    return score_value


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] == process_name:
            return process
    return None


def wait_for_benchmark_process(test_name, process_name, timeout=60):
    """Wait for the benchmark game process to start and then finish."""
    logger.info("Waiting for benchmark process '%s' to start...", process_name)

    start_time = time.time()

    while True:
        # Check if the benchmark process is running
        process = is_process_running(process_name)
        if process:
            logger.info("%s has started. Waiting for it to finish...", test_name)
            process.wait()  # This will block until the process finishes
            logger.info("Benchmark has finished.")
            break

        # If we exceed the timeout, break out of the loop and log an error
        if time.time() - start_time > timeout:
            logger.error(
                "Timeout reached while waiting for process '%s'.", process_name
            )
            raise TimeoutError(
                f"Process '{process_name}' did not start within the expected time. Is the game configured for DX12?"
            )

        # Wait for 1 second before checking again
        time.sleep(1)


def replace_exe():
    """Replaces the Strange Brigade launcher exe with the Vulkan exe for immediate launching"""
    launcher_exe = Path(EXE_PATH, "StardockLauncher.exe")
    check_backup = launcher_exe.with_name("StardockLauncher_launcher.exe")
    dx12_exe = launcher_exe.with_name("AshesEscalation_DX12.exe")
    if not check_backup.exists():
        launcher_exe.rename(check_backup)
        try:
            shutil.copy(dx12_exe, launcher_exe)
        except OSError:
            check_backup.rename(launcher_exe)
            raise
        logger.info("Replacing launcher file in %s", EXE_PATH)
    elif not launcher_exe.exists():
        shutil.copy(dx12_exe, launcher_exe)
        logger.info("Replacing launcher file in %s", EXE_PATH)
    else:
        logger.info("Launcher already replaced with DX12 exe.")


def restore_exe():
    """Restores the launcher exe back to the original exe name to close the loop."""
    launcher_exe = Path(EXE_PATH, "StardockLauncher.exe")
    check_backup = launcher_exe.with_name("StardockLauncher_launcher.exe")
    if not check_backup.exists():
        logger.info("Launcher already restored or file does not exist.")
    elif not launcher_exe.exists():
        check_backup.rename(launcher_exe)
        logger.info("Restoring launcher file in %s", EXE_PATH)
    else:
        launcher_exe.unlink()
        check_backup.rename(launcher_exe)
        logger.info("Restoring launcher file in %s", EXE_PATH)
