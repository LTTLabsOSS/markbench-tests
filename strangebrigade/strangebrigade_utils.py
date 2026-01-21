"""Utility functions for Strange Brigade test script"""
import os
import re
import logging
import sys
import shutil
from pathlib import Path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.steam import get_app_install_location

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

STEAM_GAME_ID = 312670
EXE_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "bin")
PROCESS_NAME = "StrangeBrigade.exe"
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{LOCALAPPDATA}\\Strange Brigade"
CONFIG_FILENAME = "GraphicsOptions.ini"

def read_current_resolution():
    width = 0
    height = 0
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"

    try:
        with open(cfg, encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line.startswith("Resolution_Width"):
                    try:
                        width = int(line.split("=", 1)[1])
                    except (ValueError, IndexError):
                        width = 0

                elif line.startswith("Resolution_Height"):
                    try:
                        height = int(line.split("=", 1)[1])
                    except (ValueError, IndexError):
                        height = 0

                if width and height:
                    break

    except OSError:
        # File missing, locked, unreadable, etc.
        return 0, 0

    return width, height

def replace_exe():
    """Replaces the Strange Brigade launcher exe with the Vulkan exe for immediate launching
    """
    check_backup = Path(f"{EXE_PATH}\\StrangeBrigade_launcher.exe")
    launcher_exe = Path(f"{EXE_PATH}\\StrangeBrigade.exe")
    vulkan_exe = Path(f"{EXE_PATH}\\StrangeBrigade_Vulkan.exe")
    if not os.path.exists(check_backup):
        os.rename(launcher_exe, check_backup)
        shutil.copy(vulkan_exe, launcher_exe)
        logging.info(f"Replacing launcher file in {EXE_PATH}")
    elif os.path.exists(check_backup):
        if not os.path.exists(launcher_exe):
            shutil.copy(vulkan_exe, launcher_exe)
            logging.info(f"Replacing launcher file in {EXE_PATH}")
        else:
            logging.info("Launcher already replaced with Vulkan exe.")

def restore_exe():
    """Restores the launcher exe back to the original exe name to close the loop.
    """
    check_backup = Path(f"{EXE_PATH}\\StrangeBrigade_launcher.exe")
    launcher_exe = Path(f"{EXE_PATH}\\StrangeBrigade.exe")
    if not os.path.exists(check_backup):
        logging.info(f"Launcher already restored or file does not exist.")
    elif os.path.exists(check_backup):
        if not os.path.exists(launcher_exe):
            os.rename(check_backup, launcher_exe)
            logging.info(f"Restoring launcher file in {EXE_PATH}")
        else:
            os.remove(launcher_exe)
            os.rename(check_backup, launcher_exe)
            logging.info(f"Restoring launcher file in {EXE_PATH}")