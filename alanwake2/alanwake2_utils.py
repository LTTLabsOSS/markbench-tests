"""alan wake 2 test utils"""
import winreg
import os
import logging
import re
import shutil
from pathlib import Path
import json

LOCALAPPDATA = os.getenv("LOCALAPPDATA")
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
AW2_SAVE = SCRIPT_DIRECTORY.joinpath("aw2-savegame-slot-03")
CONFIG_PATH = Path(f"{LOCALAPPDATA}\\Remedy\\AlanWake2\\renderer.ini")
DEFAULT_EXECUTABLE_NAME = "EpicGamesLauncher.exe"


def account_id() -> any:
    """get epic account id"""
    reg_path = r'Software\Epic Games\Unreal Engine\Identifiers'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "AccountId")
        winreg.CloseKey(registry_key)
        return value
    except OSError:
        return None


def get_resolution():
    """Get current resolution from settings file"""
    height_pattern = re.compile(r"\"m_iOutputResolutionY\": (\d+),")
    width_pattern = re.compile(r"\"m_iOutputResolutionX\": (\d+),")
    height = 0
    width = 0
    with open(CONFIG_PATH, encoding="utf-8") as f:
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


def copy_save() -> None:
    """copy benchmark save game files to local install"""
    save_location = Path(f"{LOCALAPPDATA}\\Remedy\\AlanWake2\\{account_id()}\\")
    is_valid_benchmark = os.path.isdir(AW2_SAVE)

    if not is_valid_benchmark:
        raise Exception(f"Can't find the benchmark folder: {AW2_SAVE}")

    # Validate/create path to directory where we will copy benchmark to
    try:
        Path(save_location).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error("Could not copy files - likely due to non-directory file existing at path.")
        raise e

    # Copy the benchmark over
    logging.info("Copying benchmark to install folder")
    destination_folder = save_location.joinpath(os.path.basename(AW2_SAVE))
    logging.info("Copying: %s -> %s", AW2_SAVE, destination_folder)
    shutil.copytree(AW2_SAVE, destination_folder, dirs_exist_ok = True)


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