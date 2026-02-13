"""Rocket League test utils"""
import winreg
import getpass
import logging
import re
import shutil
from pathlib import Path
import json

USERNAME = getpass.getuser()
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
REPLAY_LOCATION = Path(
    f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rocket League\\TAGame\\Demos")
CONFIG_PATH = Path(
    f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rocket League\\TAGame\\Config\\TASystemSettings.ini")
DEFAULT_EXECUTABLE_NAME = "EpicGamesLauncher.exe"


def get_resolution():
    """Get current resolution from settings file"""
    height_pattern = re.compile(r"^ResY=(\d+)")
    width_pattern = re.compile(r"^ResX=(\d+)")
    height = 0
    width = 0
    with CONFIG_PATH.open(encoding="utf-8") as f:
        lines = f.readlines()
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


def copy_replay() -> None:
    """Copy replay to install directory"""
    try:
        replay_file = "D83190474AB0043E7595FDB3E1EC12E0.replay"
        src_path = SCRIPT_DIRECTORY / replay_file
        REPLAY_LOCATION.mkdir(parents=True, exist_ok=True)

        dest_path = REPLAY_LOCATION / replay_file
        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
    except OSError as err:
        logging.error("Could not copy replay file")
        raise err


def find_epic_executable() -> any:
    """Get path to Epic Games Executable"""
    reg_path = r'Software\Epic Games\EOS'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "ModSdkCommand")
        winreg.CloseKey(registry_key)
        return value
    except OSError:
        return None