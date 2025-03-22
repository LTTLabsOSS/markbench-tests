"""Marvel Rivals test script utils"""
import re
import sys
from pathlib import Path
import os
import winreg
import json

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

def find_game_version() -> str:
    """Find the version of the specific game (e.g., AlanWake2) from the launcher installed data."""
    installerdat = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
    
    try:
        # Open the file and read its entire content
        with open(installerdat, encoding="utf-8") as file:
            file_content = file.read()

        # Check if the "InstallationList" section is in the content
        installation_list_match = re.search(r'"InstallationList":\s*(\[[^\]]*\])', file_content)
        if not installation_list_match:
            print("No InstallationList found.")
            return None

        # Extract the InstallationList part from the file
        installation_list_json = installation_list_match.group(1)
        
        # Load the installation list as JSON
        installation_list = json.loads(installation_list_json)

        # Loop through each item in the installation list
        for game in installation_list:
            # Check if the game's InstallLocation contains the target string (AlanWake2)
            if "MarvelRivalsjKtnW" in game.get("InstallLocation", ""):
                # Return the AppVersion for this game
                return game.get("AppVersion", None)

    except Exception as e:
        print(f"Error: {e}")

    return None