"""Utility functions for Total War: Warhammer III test script"""

import logging
import re
import shutil
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.paths import local_appdata
from harness_utils.steam import get_app_install_location

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
STEAM_GAME_ID = 949230
LOCAL_APPDATA = local_appdata(STEAM_GAME_ID)
LAUNCHCONFIG_LOCATION = LOCAL_APPDATA / "Paradox Interactive"
INSTALL_LOCATION = get_app_install_location(STEAM_GAME_ID)
CONFIG_LOCATION = (
    LOCAL_APPDATA.parent / "LocalLow" / "Colossal Order" / "Cities Skylines II"
)
SAVE_LOCATION = CONFIG_LOCATION / "Saves" / "76561199517889423"
CONFIG_FILENAME = "launcher-settings.json"
CONFIG_FULL_PATH = CONFIG_LOCATION / CONFIG_FILENAME


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    resolution_pattern = re.compile(r"\"fullscreen_resolution\"\: \"(\d+x\d+)\"\,")
    resolution = 0
    with CONFIG_FULL_PATH.open(encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = resolution_match.group(1)
    return resolution


def copy_continuegame(config_files: list[str]) -> None:
    """Copy continue game files to config directory"""
    for file in config_files:
        try:
            src_path = SCRIPT_DIRECTORY / "config" / file
            CONFIG_LOCATION.mkdir(parents=True, exist_ok=True)
            dest_path = CONFIG_LOCATION / file
            logger.info("Copying: %s -> %s", file, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logger.error("Could not copy save information files. %s", err)
            raise


def copy_launcherfiles(launcher_files: list[str]) -> None:
    """Copy launcher files to game directory"""
    for file in launcher_files:
        try:
            src_path = SCRIPT_DIRECTORY / "launcher" / file
            INSTALL_LOCATION.mkdir(parents=True, exist_ok=True)
            dest_path = INSTALL_LOCATION / file
            logger.info("Copying: %s -> %s", file, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logger.error("Could not copy launcher files %s", err)
            raise


def copy_launcherpath():
    """Write the override launcher path to the launcher config directory."""
    try:
        launcherpath = "launcherpath"
        LAUNCHCONFIG_LOCATION.mkdir(parents=True, exist_ok=True)
        dest_path = LAUNCHCONFIG_LOCATION / launcherpath
        if dest_path.exists():
            dest_path.unlink()
            logger.info("Removing old launcher file from %s", LAUNCHCONFIG_LOCATION)
        logger.info("Copying: %s -> %s", launcherpath, dest_path)
        dest_path.write_text(str(INSTALL_LOCATION), encoding="utf-8")
    except OSError as err:
        logger.error("Could not copy the launcherpath file. %s", err)
        raise


def copy_benchmarksave(save_files: list[str]) -> None:
    """Copy benchmark save file to save directory"""
    for file in save_files:
        try:
            src_path = SCRIPT_DIRECTORY / "save" / file
            SAVE_LOCATION.mkdir(parents=True, exist_ok=True)
            dest_path = SAVE_LOCATION / file
            logger.info("Copying: %s -> %s", file, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logger.error("Could not copy the save game. %s", err)
            raise
