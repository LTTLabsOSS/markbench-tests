"""Utility functions for Strange Brigade test script"""

import logging
import os
import re
import shutil
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.steam import get_app_install_location

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

STEAM_GAME_ID = 312670
EXE_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "bin")
PROCESS_NAME = "StrangeBrigade.exe"
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{LOCALAPPDATA}\\Strange Brigade"
CONFIG_FILENAME = "GraphicsOptions.ini"


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"Resolution_Width = (\d+);")
    width_pattern = re.compile(r"Resolution_Height = (\d+);")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


def replace_exe(render_engine):
    """Replaces the Strange Brigade launcher exe with the Vulkan exe for immediate launching"""
    check_backup = Path(f"{EXE_PATH}\\StrangeBrigade_launcher.exe")
    launcher_exe = Path(f"{EXE_PATH}\\StrangeBrigade.exe")
    engine = render_engine.lower()

    if engine == "vulkan":
        engine_exe = Path(f"{EXE_PATH}\\StrangeBrigade_Vulkan.exe")
    elif engine == "dx12":
        engine_exe = Path(f"{EXE_PATH}\\StrangeBrigade_DX12.exe")
    # Back up the original launcher once.
    if not check_backup.exists():
        os.rename(launcher_exe, check_backup)
        logging.info("Backed up original launcher.")

    # Always make sure the launcher points at the requested engine.
    if launcher_exe.exists():
        os.remove(launcher_exe)

    shutil.copy(engine_exe, launcher_exe)
    logging.info("Launcher replaced with %s", engine_exe.name)

    return True


def restore_exe():
    """Restores the launcher exe back to the original exe name to close the loop."""
    check_backup = Path(f"{EXE_PATH}\\StrangeBrigade_launcher.exe")
    launcher_exe = Path(f"{EXE_PATH}\\StrangeBrigade.exe")
    if not check_backup.exists():
        logging.info("No launcher backup found.")
        return

    if launcher_exe.exists():
        os.remove(launcher_exe)

    shutil.copy(check_backup, launcher_exe)

    logging.info("Original launcher restored.")
