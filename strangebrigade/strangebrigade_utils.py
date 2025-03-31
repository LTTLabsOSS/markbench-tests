"""Utility functions for Total War: Warhammer III test script"""
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

def replace_exe():
    """Removes files specified by provided list of file paths.
    Does nothing for a path that does not exist.
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