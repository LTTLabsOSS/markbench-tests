"""Utility functions related to using Steam for running games."""

import logging
import os
import re
import shutil
from pathlib import Path
from subprocess import Popen

from harness_utils.platform import is_linux, is_windows, require_linux, require_windows

logger = logging.getLogger(__name__)


def get_run_game_id_command(game_id: int) -> str:
    """Returns the steam run game id command with the given game ID"""
    command = "steam://rungameid/" + str(game_id)
    logger.debug("Generated Steam run game command game_id=%s command=%s", game_id, command)
    return command


def _read_steam_registry_value(reg_path: str, value_name: str) -> str:
    logger.info("Reading Steam registry value path=%s value=%s", reg_path, value_name)
    require_windows("Steam registry lookup")
    import winreg

    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, value_name)
    winreg.CloseKey(reg_key)
    logger.debug("Read Steam registry value path=%s value=%s result=%s", reg_path, value_name, value)
    return value


def _linux_steam_root_candidates() -> list[Path]:
    steam_dir = os.getenv("STEAM_DIR")
    if steam_dir:
        candidates = [Path(steam_dir).expanduser()]
    else:
        candidates = [Path.home() / ".local" / "share" / "Steam"]
    logger.debug("Linux Steam root candidates: %s", candidates)
    return candidates


def get_steam_library_paths() -> list[Path]:
    """Returns the configured Linux Steam library root path."""
    logger.info("Resolving Steam library paths")
    require_linux("Steam library discovery")
    paths = [Path(get_steam_folder_path())]
    logger.info("Resolved Steam library paths: %s", paths)
    return paths


def get_steam_folder_path() -> str:
    """Gets the path to the Steam installation directory."""
    logger.info("Resolving Steam folder path")
    if is_windows():
        return _read_steam_registry_value(r"Software\Valve\Steam", "SteamPath")
    if is_linux():
        for root in _linux_steam_root_candidates():
            logger.debug("Checking Linux Steam root path=%s", root)
            if root.exists():
                logger.info("Resolved Linux Steam folder path=%s", root)
                return str(root)
        checked = ", ".join(str(path) for path in _linux_steam_root_candidates())
        raise RuntimeError(f"Steam folder not found; checked: {checked}")
    raise RuntimeError("Steam folder lookup is only supported on Windows and Linux")


def get_steam_exe_path() -> str:
    """Gets the path to the Steam executable."""
    logger.info("Resolving Steam executable path")
    if is_windows():
        return _read_steam_registry_value(r"Software\Valve\Steam", "SteamExe")
    if is_linux():
        steam = shutil.which("steam")
        if steam:
            logger.info("Resolved Linux Steam executable path=%s", steam)
            return steam
        raise RuntimeError("Steam launch requires `steam` on PATH")
    raise RuntimeError("Steam executable lookup is only supported on Windows and Linux")


def get_steamapps_common_path() -> str:
    """Returns a path to the steamapps/common folder relative to the Steam installation path"""
    path = str(Path(get_steam_folder_path()) / "steamapps" / "common")
    logger.info("Resolved steamapps common path=%s", path)
    return path


def get_registry_active_user() -> int:
    """Gets the Active Process registry key to find the Steam3 ID value of the active user.
    This is needed sometimes when looking for information from local filesystems as games
    may use this value as a folder name.
    See https://developer.valvesoftware.com/wiki/SteamID for more information about ID formats.
    """
    logger.info("Reading Steam active user registry value")
    require_windows("Steam active user registry lookup")
    import winreg

    reg_path = r"Software\Valve\Steam\ActiveProcess"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, "ActiveUser")
    winreg.CloseKey(reg_key)
    logger.info("Resolved Steam active user=%s", value)
    return value


def get_app_manifest_path(app_id: int) -> Path:
    """Returns the Steam app manifest path for the given app ID."""
    logger.info("Resolving Steam app manifest path app_id=%s", app_id)
    manifest_name = f"appmanifest_{app_id}.acf"

    if is_windows():
        manifest_path = (Path(get_app_install_location(app_id)) / "../" / "../" / manifest_name).resolve()
        logger.info("Resolved Windows Steam app manifest path app_id=%s path=%s", app_id, manifest_path)
        return manifest_path

    if is_linux():
        manifest_path = Path(get_steam_folder_path()) / "steamapps" / manifest_name
        logger.debug("Checking Linux Steam app manifest path=%s", manifest_path)
        if manifest_path.exists():
            logger.info("Resolved Linux Steam app manifest path app_id=%s path=%s", app_id, manifest_path)
            return manifest_path
        raise RuntimeError(f"Steam app manifest not found: {manifest_path}")

    raise RuntimeError("Steam app manifest lookup is only supported on Windows and Linux")


def _read_app_manifest_value(manifest_path: Path, value_name: str) -> str | None:
    logger.info("Reading Steam app manifest value path=%s value=%s", manifest_path, value_name)
    with open(manifest_path, encoding="utf-8") as file:
        data = file.read()
    value_match = re.search(rf'"{re.escape(value_name)}"\s*"([^"]+)"', data)
    if value_match is None:
        return None
    return value_match.group(1)


def get_app_install_location(app_id: int) -> str:
    """Given the Steam App ID, gets the install directory."""
    logger.info("Resolving Steam app install location app_id=%s", app_id)
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
        logger.info("Resolved Windows Steam app install location app_id=%s path=%s", app_id, value)
        return value

    if is_linux():
        manifest_path = get_app_manifest_path(app_id)
        install_dir = _read_app_manifest_value(manifest_path, "installdir")
        if not install_dir:
            raise RuntimeError(f"Steam app manifest missing installdir: {manifest_path}")
        path = str(manifest_path.parent / "common" / install_dir)
        logger.info("Resolved Linux Steam app install location app_id=%s path=%s", app_id, path)
        return path

    raise RuntimeError("Steam app install lookup is only supported on Windows and Linux")


def get_proton_prefix(app_id: int) -> Path:
    """Returns the Proton prefix path for a Steam app."""
    logger.info("Resolving Proton prefix app_id=%s", app_id)
    require_linux("Proton prefix lookup")
    path = get_app_manifest_path(app_id).parent / "compatdata" / str(app_id) / "pfx"
    logger.info("Resolved Proton prefix app_id=%s path=%s", app_id, path)
    return path


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
    logger.info("Launching Steam run command: %s %s", steam_path, steam_run_arg)
    return Popen([steam_path, steam_run_arg])


def exec_steam_game(game_id: int, steam_path=None, game_params=None) -> Popen:
    """Runs a game by providing steam executable with an array of parameters.
    The `steam_path` argument can be used to specify a specific path to the Steam executable
    instead of relying on finding the current installation in the Window's registry.
    """
    if game_params is None:
        game_params = []

    if steam_path is None and is_linux():
        command = [get_steam_exe_path(), "-applaunch", str(game_id), *game_params]
        logger.info("Built Linux Steam command: %s", " ".join(command))
    else:
        if steam_path is None:
            steam_path = get_steam_exe_path()
        command = [steam_path, "-applaunch", str(game_id)] + game_params

    logger.info("Launching Steam game command: %s", ", ".join(command))
    return Popen(command)


def get_build_id(game_id: int) -> str | None:
    """Gets the build ID of a game from the Steam installation directory"""
    logger.info("Resolving Steam build ID game_id=%s", game_id)

    if is_windows() or is_linux():
        manifest_path = get_app_manifest_path(game_id)
        logger.debug("Checking Steam build ID manifest path=%s", manifest_path)
        if not manifest_path.exists():
            logger.warning("Game folder not found when looking for game version")
            return None
        build_id = _read_app_manifest_value(manifest_path, "buildid")
        if build_id is not None:
            logger.info("Resolved Steam build ID game_id=%s build_id=%s", game_id, build_id)
            return build_id
        logger.warning("No 'buildid' found in the file when looking for game version")
        return None

    raise RuntimeError("Steam build ID lookup is only supported on Windows and Linux")
