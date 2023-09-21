import logging
import os
from pathlib import Path
import shutil
import re
import winreg

from harness_utils.steam import get_registry_active_user, get_steam_folder_path

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
STEAM_GAME_ID = 730
CSGO_BENCHMARK = os.path.join(SCRIPT_DIRECTORY, "CSGO")
STEAM_USER_ID = get_registry_active_user()


config_path = f"{get_steam_folder_path()}\\userdata\\{STEAM_USER_ID}\\{STEAM_GAME_ID}\\local\\cfg\\video.txt"


def InstallLocation() -> any:
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 730'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def get_resolution():
    height_pattern = re.compile(r"\"setting.defaultresheight\"		\"(\d+)\"")
    width_pattern = re.compile(r"\"setting.defaultres\"		\"(\d+)\"")
    cfg = f"{config_path}"
    height = 0
    width = 0
    with open(cfg) as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)


def copy_benchmark() -> None:
    is_valid_benchmark = os.path.isdir(CSGO_BENCHMARK)

    if not is_valid_benchmark:
        raise Exception(f"Can't find the benchmark folder: {CSGO_BENCHMARK}")

    # Validate/create path to directory where we will copy benchmark to
    dest_dir: str = InstallLocation()
    try:
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error("Could not copy files - likely due to non-directory file existing at path.")
        raise e
    
    # Copy the benchmark over
    logging.info("Copying benchmark to install folder")
    destination_folder = os.path.join(dest_dir, os.path.basename(CSGO_BENCHMARK))
    logging.info(F"Copying: {CSGO_BENCHMARK} -> {destination_folder}")
    shutil.copytree(CSGO_BENCHMARK, destination_folder, dirs_exist_ok = True)
