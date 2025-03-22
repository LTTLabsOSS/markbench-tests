"""Marvel Rivals test script utils"""
import re
import sys
from pathlib import Path
import os
import winreg
import win32api

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

STEAM_GAME_ID = 730
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\Marvel\\Saved\\Config\\Windows"
CONFIG_FILENAME = "GameUserSettings.ini"


def read_resolution():
    """Gets resolution width and height values from local file"""
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)

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

def find_game_exe() -> str:
    installerdat = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
    gamepath = re.compile(r'"InstallLocation":\s*"([^"]*MarvelRivalsjKtnW[^"]*)"')
    gamepath_found = None
    with open(installerdat, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            gamepath_find = gamepath.search(line)
            if gamepath_find is not None:
                gamepath_found = gamepath_find.group(1)
                break
    return gamepath_found

def find_game_version() -> str:
    """get current Marvel Rivals version string"""
    marvel_exe_path = find_game_exe()
    if not marvel_exe_path:
        print("Marvel Rivals installation not found!")
        return None  # Exit early if path is not found
    path = rf"{marvel_exe_path}\MarvelGame\Marvel\Binaries\Win64\Marvel-Win64-Shipping.exe"
    try:
        lang, codepage = win32api.GetFileVersionInfo(path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        full_version = win32api.GetFileVersionInfo(path, str_info_path)

        # Trim to first three segments if an extra one exists
        version_parts = full_version.split(".")
        if len(version_parts) > 3:
            return ".".join(version_parts[:3])  # Keep only first three parts
        
        return full_version  # Return as is if it's already correct
    except Exception as e:
        print(f"Error retrieving game version {e}")
        return None