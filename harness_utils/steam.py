"""Utility functions related to using Steam for running games."""
import logging
import winreg
from subprocess import Popen
from pathlib import Path
import re


def get_run_game_id_command(game_id: int) -> str:
    """Returns the steam run game id command with the given game ID"""
    return "steam://rungameid/" + str(game_id)


def get_steam_folder_path() -> str:
    """Gets the path to the Steam installation directory from the SteamPath registry key"""
    reg_path = r"Software\Valve\Steam"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _  = winreg.QueryValueEx(reg_key, "SteamPath")
    return value


def get_steam_exe_path() -> str:
    """Gets the path to the Steam executable from the SteamExe registry key"""
    reg_path = r"Software\Valve\Steam"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _  = winreg.QueryValueEx(reg_key, "SteamExe")
    return value


def get_steamapps_common_path() -> str:
    """Returns a path to the steamapps/common folder relative to the Steam installation path"""
    return str(Path(get_steam_folder_path()) / "steamapps" / "common")


def get_registry_active_user() -> int:
    """Gets the Active Process registry key to find the Steam3 ID value of the active user.
    This is needed sometimes when looking for information from local filesystems as games
    may use this value as a folder name.
    See https://developer.valvesoftware.com/wiki/SteamID for more information about ID formats.
    """
    reg_path = r"Software\Valve\Steam\ActiveProcess"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _  = winreg.QueryValueEx(reg_key, "ActiveUser")
    return value


def get_app_install_location(app_id: int) -> str:
    """Given the Steam App ID, Gets the install directory from the Windows Registry"""
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App " + str(app_id)
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
    winreg.CloseKey(registry_key)
    return value


def exec_steam_run_command(game_id: int, steam_path=None) -> Popen:
    """Runs a game using the Steam browser protocol. The `steam_path` argument can be used to
    specify a specific path to the Steam executable instead of relying on finding the current
    installation in the Window's registry.

    To launch a game with provided arguments,
    see the function `exec_steam_game`.
    """
    steam_run_arg = "steam://rungameid/" + str(game_id)
    if steam_path is None:
        steam_path = get_steam_exe_path()
    logging.info("%s %s", steam_path, steam_run_arg)
    return Popen([steam_path, steam_run_arg])


def exec_steam_game(game_id: int, steam_path=None, game_params=None) -> Popen:
    """Runs a game by providing steam executable with an array of parameters.
    The `steam_path` argument can be used to specify a specific path to the Steam executable
    instead of relying on finding the current installation in the Window's registry.
    """
    if steam_path is None:
        steam_path = get_steam_exe_path()
    if game_params is None:
        game_params = []
    command = [steam_path, "-applaunch", str(game_id)] + game_params
    logging.info(", ".join(command))
    return Popen(command)

def get_build_id(game_id: int) -> str:
    """Gets the build ID of a game from the Steam installation directory"""
    game_folder = Path(get_app_install_location(game_id)) / "../" / "../" / f"appmanifest_{game_id}.acf"
    if not game_folder.exists():
        logging.warning("Game folder not found when looking for game version")
        return None
    with open(game_folder, 'r', encoding='utf-8') as file:
        data = file.read()
    buildid_match = re.search(r'"buildid"\s*"(\d+)"', data)
    if buildid_match is not None:
        return buildid_match.group(1)
    logging.warning("No 'buildid' found in the file when looking for game version")
    return None
