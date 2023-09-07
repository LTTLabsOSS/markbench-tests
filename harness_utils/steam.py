import os
import winreg

DEFAULT_BASE_PATH = os.path.join(os.environ["ProgramFiles(x86)"], "Steam")
DEFAULT_EXECUTABLE_NAME = "Steam.exe"
DEFAULT_EXECUTABLE_PATH = os.path.join(
    DEFAULT_BASE_PATH, DEFAULT_EXECUTABLE_NAME)
DEFAULT_STEAMAPPS_COMMON_PATH = os.path.join(
    DEFAULT_BASE_PATH, "steamapps", "common")


def get_run_game_id_command(id: int) -> str:
    return "steam://rungameid/" + str(id)


def get_registry_active_user() -> int:
    """
    Gets the Active Process registry key to find the Steam3 ID value of the active user.
    This is needed sometimes when looking for information from local filesystems as game may use this value as a folder name.
    See https://developer.valvesoftware.com/wiki/SteamID for more information about ID formats.
    """
    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    key = winreg.OpenKey(registry, "Software\Valve\Steam\ActiveProcess")
    active_user_key = winreg.QueryValueEx(key, "ActiveUser")
    return active_user_key[0]
