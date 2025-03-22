"""Rocket League test utils"""
from argparse import ArgumentParser
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
            if "rocketleague" in game.get("InstallLocation", ""):
                # Return the AppVersion for this game
                return game.get("AppVersion", None)

    except Exception as e:
        print(f"Error: {e}")

    return None