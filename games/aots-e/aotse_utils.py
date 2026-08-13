"""Utility functions for Ashes of the Singularity: Escalation test script"""

import logging
import re
import shutil
import sys
from pathlib import Path

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
    user_documents(STEAM_GAME_ID)
    / ("my games" if sys.platform == "linux" else "My Games")
    / "Ashes of the Singularity - Escalation"
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
                try:
                    width = int(resolution_match.group(1))
                    height = int(resolution_match.group(2))
                except ValueError:
                    logger.warning("Ignoring invalid resolution: %s", line.strip())
    return width, height


def delete_old_scores(file):
    """Deletes old score files based on a given pattern"""
    for thefile in CONFIG_PATH.glob(file):
        thefile.unlink()
        logger.info("Deleted old score file: %s", thefile)


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


def replace_exe():
    """Replaces the Strange Brigade launcher exe with the Vulkan exe for immediate launching"""
    backup_launcher_exe = EXE_PATH / "StardockLauncher_launcher.exe"
    original_launcher_exe = EXE_PATH / "StardockLauncher.exe"
    dx12_exe = EXE_PATH / "AshesEscalation_DX12.exe"

    if not backup_launcher_exe.exists():
        shutil.copy(original_launcher_exe, backup_launcher_exe)

    shutil.copy(dx12_exe,original_launcher_exe)

def restore_exe():
    """Restores the launcher exe back to the original exe name to close the loop."""
    backup_launcher_exe = EXE_PATH / "StardockLauncher_launcher.exe"
    original_launcher_exe = EXE_PATH / "StardockLauncher.exe"
    if not backup_launcher_exe.exists():
        logger.error("backup launcher exe does not exist")
    else:
        shutil.copy(backup_launcher_exe,original_launcher_exe)
        logger.debug("restored launcher")
