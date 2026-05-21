"""Utility functions related to using Steam for running games."""

import logging
import os
import re
import shutil
from pathlib import Path
from subprocess import Popen
from typing import Any

from harness_utils.platform import is_linux, is_windows, require_linux, require_windows


def get_run_game_id_command(game_id: int) -> str:
    """Returns the steam run game id command with the given game ID"""
    return "steam://rungameid/" + str(game_id)


def _read_steam_registry_value(reg_path: str, value_name: str) -> str:
    require_windows("Steam registry lookup")
    import winreg

    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, value_name)
    winreg.CloseKey(reg_key)
    return value


def _linux_steam_root_candidates() -> list[Path]:
    steam_dir = os.getenv("STEAM_DIR")
    if steam_dir:
        return [Path(steam_dir).expanduser()]
    return [Path.home() / ".local" / "share" / "Steam"]


def _load_vdf(path: Path) -> dict[str, Any]:
    import vdf

    with open(path, encoding="utf-8") as file:
        return vdf.load(file)


def get_steam_library_paths() -> list[Path]:
    """Returns the configured Linux Steam library root path."""
    require_linux("Steam library discovery")
    return [Path(get_steam_folder_path())]


def get_steam_folder_path() -> str:
    """Gets the path to the Steam installation directory."""
    if is_windows():
        return _read_steam_registry_value(r"Software\Valve\Steam", "SteamPath")
    if is_linux():
        for root in _linux_steam_root_candidates():
            if root.exists():
                return str(root)
        checked = ", ".join(str(path) for path in _linux_steam_root_candidates())
        raise RuntimeError(f"Steam folder not found; checked: {checked}")
    raise RuntimeError("Steam folder lookup is only supported on Windows and Linux")


def get_steam_exe_path() -> str:
    """Gets the path to the Steam executable."""
    if is_windows():
        return _read_steam_registry_value(r"Software\Valve\Steam", "SteamExe")
    if is_linux():
        steam = shutil.which("steam")
        if steam:
            return steam
        raise RuntimeError("Steam launch requires `steam` on PATH")
    raise RuntimeError("Steam executable lookup is only supported on Windows and Linux")


def get_steamapps_common_path() -> str:
    """Returns a path to the steamapps/common folder relative to the Steam installation path"""
    return str(Path(get_steam_folder_path()) / "steamapps" / "common")


def get_registry_active_user() -> int:
    """Gets the Active Process registry key to find the Steam3 ID value of the active user.
    This is needed sometimes when looking for information from local filesystems as games
    may use this value as a folder name.
    See https://developer.valvesoftware.com/wiki/SteamID for more information about ID formats.
    """
    require_windows("Steam active user registry lookup")
    import winreg

    reg_path = r"Software\Valve\Steam\ActiveProcess"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, "ActiveUser")
    winreg.CloseKey(reg_key)
    return value


def get_app_manifest_path(app_id: int) -> Path:
    """Returns the Steam app manifest path for the given app ID."""
    manifest_name = f"appmanifest_{app_id}.acf"

    if is_windows():
        return (Path(get_app_install_location(app_id)) / "../" / "../" / manifest_name).resolve()

    if is_linux():
        manifest_path = Path(get_steam_folder_path()) / "steamapps" / manifest_name
        if manifest_path.exists():
            return manifest_path
        raise RuntimeError(f"Steam app manifest not found: {manifest_path}")

    raise RuntimeError("Steam app manifest lookup is only supported on Windows and Linux")


def _get_app_state(app_id: int) -> dict[str, Any]:
    manifest_path = get_app_manifest_path(app_id)
    data = _load_vdf(manifest_path)
    app_state = data.get("AppState") or data.get("appstate")
    if not isinstance(app_state, dict):
        raise RuntimeError(f"Steam app manifest missing AppState: {manifest_path}")
    return app_state


def get_app_install_location(app_id: int) -> str:
    """Given the Steam App ID, Gets the install directory from the Windows Registry"""
    if is_windows():
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App " + str(
            app_id
        )
        require_windows("Steam app install registry lookup")
        import winreg

        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value

    if is_linux():
        manifest_path = get_app_manifest_path(app_id)
        app_state = _get_app_state(app_id)
        install_dir = app_state.get("installdir")
        if not install_dir:
            raise RuntimeError(f"Steam app manifest missing installdir: {manifest_path}")
        return str(Path(get_steam_folder_path()) / "steamapps" / "common" / install_dir)

    raise RuntimeError("Steam app install lookup is only supported on Windows and Linux")


def get_proton_prefix(app_id: int) -> Path:
    """Returns the Proton prefix path for a Steam app."""
    require_linux("Proton prefix lookup")
    return Path(get_steam_folder_path()) / "steamapps" / "compatdata" / str(app_id) / "pfx"


def _linux_steam_command(game_id: int, game_params: list[str] | None = None) -> list[str]:
    if game_params is None:
        game_params = []
    return [get_steam_exe_path(), "-applaunch", str(game_id), *game_params]


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
    if game_params is None:
        game_params = []

    if steam_path is None and is_linux():
        command = _linux_steam_command(game_id, game_params)
    else:
        if steam_path is None:
            steam_path = get_steam_exe_path()
        command = [steam_path, "-applaunch", str(game_id)] + game_params

    logging.info(", ".join(command))
    return Popen(command)


def get_build_id(game_id: int) -> str | None:
    """Gets the build ID of a game from the Steam installation directory"""
    if is_windows():
        game_folder = (
            Path(get_app_install_location(game_id))
            / "../"
            / "../"
            / f"appmanifest_{game_id}.acf"
        )
        if not game_folder.exists():
            logging.warning("Game folder not found when looking for game version")
            return None
        with open(game_folder, "r", encoding="utf-8") as file:
            data = file.read()
        buildid_match = re.search(r'"buildid"\s*"(\d+)"', data)
        if buildid_match is not None:
            return buildid_match.group(1)
        logging.warning("No 'buildid' found in the file when looking for game version")
        return None

    if is_linux():
        manifest_path = get_app_manifest_path(game_id)
        if not manifest_path.exists():
            logging.warning("Game folder not found when looking for game version")
            return None
        app_state = _get_app_state(game_id)
        build_id = app_state.get("buildid")
        if build_id is not None:
            return str(build_id)
        logging.warning("No 'buildid' found in the file when looking for game version")
        return None

    raise RuntimeError("Steam build ID lookup is only supported on Windows and Linux")
