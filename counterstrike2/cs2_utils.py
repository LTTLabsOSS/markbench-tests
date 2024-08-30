"""Counter-Strike 2 test script utils"""
from argparse import ArgumentParser
import logging
import re
import shutil
import sys
from pathlib import Path

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.steam import get_app_install_location, get_registry_active_user, get_steam_folder_path

STEAM_GAME_ID = 730
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_USER_ID = get_registry_active_user()
DEFAULT_INSTALL_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive")


def get_install_path():
    """Gets install path for Counter-Strike 2"""
    install_path = get_app_install_location(STEAM_GAME_ID)
    if not install_path:
        return DEFAULT_INSTALL_PATH
    return install_path


def copy_config() -> None:
    """Copy benchmark config to cs2 2 folder"""
    try:
        config_path = Path(get_install_path(), "game\\csgo\\")
        config_path.mkdir(parents=True, exist_ok=True)
        src_path = SCRIPT_DIRECTORY / "csgo"
        dest_path = config_path
        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        logging.info("Copying: %s -> %s", src_path, dest_path)
    except OSError as err:
        logging.info("Copying: %s -> %s", src_path, dest_path)
        logging.error("Could not copy config files.")
        raise err


def read_config() -> list[str] | None:
    """Looks for config file and returns contents if found"""
    userdata_path = Path(get_steam_folder_path(), "userdata", str(STEAM_USER_ID), str(STEAM_GAME_ID), "local", "cfg", "cs2_video.txt")
    install_path = Path(get_install_path(), "game", "csgo", "cfg", "video.txt")
    try:
        with open(userdata_path, encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        logging.error("Did not find config file at path %s. Trying path %s", userdata_path, install_path)
    try:
        with open(install_path, encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        logging.error("Did not find config file at path %s", install_path)
    return None


def get_resolution():
    """Get current resolution from settings file"""
    height_pattern = re.compile(r"\"setting.defaultresheight\"		\"(\d+)\"")
    width_pattern = re.compile(r"\"setting.defaultres\"		\"(\d+)\"")
    height = 0
    width = 0
    lines = read_config()

    if lines is None:
        logging.error("Could not find the video config file.")
        return (height, width)

    for line in lines:
        height_match = height_pattern.search(line)
        width_match = width_pattern.search(line)
        if height_match is not None:
            height = height_match.group(1)
        if width_match is not None:
            width = width_match.group(1)
        if height != 0 and width !=0:
            return (height, width)
    return (height, width)
