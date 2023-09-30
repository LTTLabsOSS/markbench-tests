"""Utility functions related to using Steam for running games."""
import logging
import os
import shutil
if os.name == 'nt':
    import winreg
else:
    import vdf
from subprocess import Popen
from pathlib import Path


def get_run_game_id_command(game_id: int) -> str:
    """Returns the steam run game id command with the given game ID"""
    return "steam://rungameid/" + str(game_id)


def get_steam_folder_path() -> str:
    """
    Gets the path to the Steam installation directory from the SteamPath registry key
    on Windows. On Linux, returns :code:`~/.steam/steam/` as that is the default
    installation location.
    """
    if os.name == 'nt':
        reg_path = r"Software\Valve\Steam"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(reg_key, "SteamPath")
        return value
    else:
        return os.path.expanduser("~/.steam/steam")


def get_steam_exe() -> str | list[str]:
    """
    On Windows, gets the path to the Steam executable from the SteamExe registry key.

    On Linux, we first use :code:`which` to check if the system-wide version of Steam
    is installed. If not, we then check if the flatpak is installed, and finally if the
    snap is installed.
    """
    if os.name == 'nt':
        reg_path = r"Software\Valve\Steam"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(reg_key, "SteamExe")
        return value
    else:
        steam_path = shutil.which("steam")
        if steam_path is not None:
            return steam_path
        else:
            flatpak_path = shutil.which("flatpak")
            if flatpak_path is not None:
                return [flatpak_path, "run", "com.valvesoftware.Steam"]
            else:
                snap_path = shutil.which("snap")
                if snap_path is not None:
                    return [snap_path, "run", "steam"]
                else:
                    raise FileNotFoundError("Could not find a steam installation on your PATH")


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
    """
    Given the Steam App ID, Gets the install directory from the Windows Registry

    On Linux, parses the libraryfolders.vdf folder to find the app install location.
    """

    if os.name == 'nt':
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App " + str(app_id)
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    else:
        with open(Path(get_steam_folder_path()) / "config" / "libraryfolders.vdf") as f:
            database = vdf.load(f)
            folders = database["libraryfolders"]
            for index, data in folders.items():
                apps = data["apps"]
                if str(app_id) in apps.keys():
                    lib_folder = Path(data["path"])
                    with open(lib_folder / "steamapps" / f"appmanifest_{app_id}.acf") as app_acf:
                        app_database = vdf.load(app_acf)
                        return (lib_folder / "steamapps" / "common" / app_database["AppState"]["installdir"]).absolute()


def exec_steam_run_command(game_id: int, steam_command: str | list = None) -> Popen:
    """Runs a game using the Steam browser protocol. The `steam_path` argument can be used to
    specify a specifc path to the Steam executable instead of relying on finding the current
    installation in the Window's registry.
    
    To launch a game with provided arguments,
    see the function `exec_steam_game`.
    """
    steam_run_arg = "steam://rungameid/" + str(game_id)
    if steam_command is None:
        steam_command = get_steam_exe()
    logging.info("%s %s", steam_command, steam_run_arg)
    if isinstance(steam_command, str):
        return Popen([steam_command, steam_run_arg])
    else:
        steam_command.append(steam_run_arg)
        return Popen(steam_command)


def exec_steam_game(game_id: int, steam_path=None, game_params=None) -> Popen:
    """Runs a game by providing steam executable with an array of parameters.
    The `steam_path` argument can be used to specify a specifc path to the Steam executable
    instead of relying on finding the current installation in the Window's registry.
    """
    if steam_path is None:
        steam_path = get_steam_exe()
    if game_params is None:
        game_params = []
    command = [steam_path, "-applaunch", str(game_id)] + game_params
    logging.info(", ".join(command))
    return Popen(command)
