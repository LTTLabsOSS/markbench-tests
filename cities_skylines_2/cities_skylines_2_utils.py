"""Utility functions for Total War: Warhammer III test script"""
import os
import re
import sys
import logging
import shutil
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.steam import get_app_install_location

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_GAME_ID = 949230
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
LAUNCHCONFIG_LOCATION = Path(f"{LOCALAPPDATA}\\Paradox Interactive")
INSTALL_LOCATION = Path(get_app_install_location(STEAM_GAME_ID))
APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = Path(f"{APPDATA}\\..\\LocalLow\\Colossal Order\\Cities Skylines II")
SAVE_LOCATION = Path(f"{CONFIG_LOCATION}\\Saves\\76561199517889423")
CONFIG_FILENAME = "launcher-settings.json"


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    resolution_pattern = re.compile(r"\"fullscreen_resolution\"\: \"(\d+x\d+)\"\,")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    resolution = 0
    with open(cfg, encoding="utf-8") as file:
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
            logging.info("Copying: %s -> %s", file, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logging.error("Could not copy save information files. %s", err)
            raise err


def copy_launcherfiles(launcher_files: list[str]) -> None:
    """Copy launcher files to game directory"""
    for file in launcher_files:
        try:
            src_path = SCRIPT_DIRECTORY / "launcher" / file
            INSTALL_LOCATION.mkdir(parents=True, exist_ok=True)
            dest_path = INSTALL_LOCATION / file
            logging.info("Copying: %s -> %s", file, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logging.error("Could not copy launcher files %s", err)
            raise err


def copy_launcherpath():
    """Copy the override launcherpath file to launcherpath directory"""
    try:
        launcherpath = "launcherpath"
        src_path = SCRIPT_DIRECTORY / "launcher" / launcherpath
        LAUNCHCONFIG_LOCATION.mkdir(parents=True, exist_ok=True)
        dest_path = LAUNCHCONFIG_LOCATION / launcherpath
        if os.path.exists(dest_path) is True:
            try:
                file_path = os.path.join(LAUNCHCONFIG_LOCATION, launcherpath)
                os.remove(file_path)
                logging.info("Removing old launcher file from %s", LAUNCHCONFIG_LOCATION)
            except OSError as e:
                logging.error("The following error occurred while trying to remove the launcherpath file: %s.", e)
        logging.info("Copying: %s -> %s", launcherpath, dest_path)
        with open(f"{src_path}", "w", encoding="utf-8") as f:
            f.write(f"{INSTALL_LOCATION}")
        shutil.copy(src_path, dest_path)
        #os.chmod(dest_path, stat.S_IREAD)
    except OSError as err:
        logging.error("Could not copy the launcherpath file. %s", err)
        raise err


def copy_benchmarksave(save_files: list[str]) -> None:
    """Copy benchmark save file to save directory"""
    for file in save_files:
        try:
            src_path = SCRIPT_DIRECTORY / "save" / file
            SAVE_LOCATION.mkdir(parents=True, exist_ok=True)
            dest_path = SAVE_LOCATION / file
            logging.info("Copying: %s -> %s", file, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logging.error("Could not copy the save game. %s", err)
            raise err
