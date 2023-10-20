"""Rocket League test utils"""
from argparse import ArgumentParser
import winreg
import os
import logging
import re
import shutil
from pathlib import Path

USERNAME = os.getlogin()
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
REPLAY_LOCATION = f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rocket League\\TAGame\\Demos"
config_path = f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rocket League\\TAGame\\Config\\TASystemSettings.ini"
DEFAULT_EXECUTABLE_NAME = "EpicGamesLauncher.exe"

def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()

def get_resolution():
    """Get current resolution from settings file"""
    height_pattern = re.compile(r"^ResY=(\d+)")
    width_pattern = re.compile(r"^ResX=(\d+)")
    cfg = f"{config_path}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as f:
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
    src_file = os.path.join(SCRIPT_DIRECTORY, "D83190474AB0043E7595FDB3E1EC12E0.replay")
    is_valid_replay = os.path.isfile(src_file)
    if not is_valid_replay:
        raise Exception(f"Can't find replay file: {src_file}")
    try:
        Path(REPLAY_LOCATION).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error(
            "Could not directory - likely due to non-directory file existing at path.")
        raise e

    # Copy the replay over
    destination_file = os.path.join(REPLAY_LOCATION, os.path.basename(src_file))
    logging.info("Copying: %s -> %s", src_file, destination_file)
    shutil.copy(src_file, destination_file)

def find_rocketleague_executable() -> any:
    """Get path to rocket league executable"""
    reg_path = r'Software\Epic Games\EOS'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "ModSdkCommand")
        winreg.CloseKey(registry_key)
        return value
    # pylint:disable=undefined-variable
    except WindowsError:
        return None
