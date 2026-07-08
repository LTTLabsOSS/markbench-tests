"""Utility functions related to using Steam for running games."""

import logging
import os
import shutil
from importlib import import_module
from pathlib import Path
from subprocess import Popen

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

WINDOWS_STEAM_ROOT = Path(r"C:\Program Files (x86)\Steam")
WINDOWS_STEAM_EXE = WINDOWS_STEAM_ROOT / "steam.exe"
STEAMID64_ACCOUNT_ID_OFFSET = 76561197960265728


def get_run_game_id_command(game_id: int) -> str:
    """Returns the steam run game id command with the given game ID"""
    command = "steam://rungameid/" + str(game_id)
    logger.debug(
        "Generated Steam run game command game_id=%s command=%s", game_id, command
    )
    return command


def _linux_steam_root() -> Path:
    import pwd

    username = pwd.getpwuid(os.getuid()).pw_name
    path = Path("/home") / username / ".local" / "share" / "Steam"
    logger.debug("Linux Steam root path: %s", path)
    return path


def _load_vdf_file(file_path: Path, description: str) -> dict:
    vdf = import_module("vdf")
    try:
        with open(file_path, encoding="utf-8") as file:
            return vdf.load(file)
    except OSError as err:
        raise RuntimeError(f"Could not read {description}: {file_path}") from err


def _get_vdf_value(data: dict, key: str):
    for current_key, value in data.items():
        if current_key.lower() == key.lower():
            return value
    return None


def _steamid64_to_account_id(steamid64: str) -> int:
    try:
        account_id = int(steamid64) - STEAMID64_ACCOUNT_ID_OFFSET
    except ValueError as err:
        raise RuntimeError(f"Invalid SteamID64: {steamid64}") from err
    if account_id < 0:
        raise RuntimeError(f"Invalid SteamID64: {steamid64}")
    return account_id


def _windows_library_folders() -> list[Path]:
    paths = [WINDOWS_STEAM_ROOT]
    library_files = [
        WINDOWS_STEAM_ROOT / "steamapps" / "libraryfolders.vdf",
        WINDOWS_STEAM_ROOT / "config" / "libraryfolders.vdf",
    ]

    for library_file in library_files:
        if not library_file.exists():
            continue
        data = _load_vdf_file(library_file, "Steam library folders file")
        library_folders = _get_vdf_value(data, "libraryfolders")
        if not isinstance(library_folders, dict):
            continue
        for index, library_folder in library_folders.items():
            if isinstance(library_folder, dict):
                library_path = _get_vdf_value(library_folder, "path")
            elif str(index).isdigit() and isinstance(library_folder, str):
                library_path = library_folder
            else:
                library_path = None
            if library_path:
                path = Path(library_path)
                if path not in paths:
                    paths.append(path)
    return paths


def get_steam_library_paths() -> list[Path]:
    """Returns the configured Steam library root paths."""
    logger.info("Resolving Steam library paths")
    if is_windows():
        paths = _windows_library_folders()
    elif is_linux():
        paths = [Path(get_steam_folder_path())]
    else:
        raise RuntimeError(
            "Steam library lookup is only supported on Windows and Linux"
        )
    logger.info("Resolved Steam library paths: %s", paths)
    return paths


def get_steam_folder_path() -> str:
    """Gets the path to the Steam installation directory."""
    logger.info("Resolving Steam folder path")
    if is_windows():
        logger.info("Using default Windows Steam folder path=%s", WINDOWS_STEAM_ROOT)
        return str(WINDOWS_STEAM_ROOT)
    if is_linux():
        root = _linux_steam_root()
        logger.info("Resolved Linux Steam folder path=%s", root)
        return str(root)
    raise RuntimeError("Steam folder lookup is only supported on Windows and Linux")


def get_steam_exe_path() -> str:
    """Gets the path to the Steam executable."""
    logger.info("Resolving Steam executable path")
    if is_windows():
        logger.info("Using default Windows Steam executable path=%s", WINDOWS_STEAM_EXE)
        return str(WINDOWS_STEAM_EXE)
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
    """Returns the most recent Steam user's Steam3 account ID.

    Steam stores users as SteamID64 values in loginusers.vdf, while userdata folders
    use the Steam3 account ID value.
    """
    logger.info("Resolving most recent Steam user")
    if not is_windows():
        raise RuntimeError("Steam active user lookup requires Windows")
    login_users_path = WINDOWS_STEAM_ROOT / "config" / "loginusers.vdf"
    data = _load_vdf_file(login_users_path, "Steam login users file")
    users = _get_vdf_value(data, "users")
    if not isinstance(users, dict):
        raise RuntimeError(f"Steam login users file missing users: {login_users_path}")

    for steamid64, user in users.items():
        if isinstance(user, dict) and _get_vdf_value(user, "MostRecent") == "1":
            account_id = _steamid64_to_account_id(steamid64)
            logger.info(
                "Resolved Steam active user=%s steamid64=%s", account_id, steamid64
            )
            return account_id

    raise RuntimeError(f"No most recent Steam user found in: {login_users_path}")


def get_app_manifest_path(app_id: int) -> Path:
    """Returns the Steam app manifest path for the given app ID."""
    logger.info("Resolving Steam app manifest path app_id=%s", app_id)
    manifest_name = f"appmanifest_{app_id}.acf"

    for library_path in get_steam_library_paths():
        manifest_path = library_path / "steamapps" / manifest_name
        logger.debug("Checking Steam app manifest path=%s", manifest_path)
        if manifest_path.exists():
            logger.info(
                "Resolved Steam app manifest path app_id=%s path=%s",
                app_id,
                manifest_path,
            )
            return manifest_path

    raise RuntimeError(f"Steam app manifest not found for app_id={app_id}")


def _read_app_manifest_value(manifest_path: Path, value_name: str) -> str | None:
    logger.info(
        "Reading Steam app manifest value path=%s value=%s", manifest_path, value_name
    )
    data = _load_vdf_file(manifest_path, "Steam app manifest")
    app_state = _get_vdf_value(data, "AppState")
    if not isinstance(app_state, dict):
        return None
    return _get_vdf_value(app_state, value_name)


def get_app_install_location(app_id: int) -> str:
    """Given the Steam App ID, gets the install directory."""
    logger.info("Resolving Steam app install location app_id=%s", app_id)
    manifest_path = get_app_manifest_path(app_id)
    install_dir = _read_app_manifest_value(manifest_path, "installdir")
    if not install_dir:
        raise RuntimeError(f"Steam app manifest missing installdir: {manifest_path}")
    path = str(manifest_path.parent / "common" / install_dir)
    logger.info("Resolved Steam app install location app_id=%s path=%s", app_id, path)
    return path


def get_proton_prefix(app_id: int) -> Path:
    """Returns the Proton prefix path for a Steam app."""
    logger.info("Resolving Proton prefix app_id=%s", app_id)
    if not is_linux():
        raise RuntimeError("Proton prefix lookup requires Linux")
    path = get_app_manifest_path(app_id).parent / "compatdata" / str(app_id) / "pfx"
    logger.info("Resolved Proton prefix app_id=%s path=%s", app_id, path)
    return path


def exec_steam_run_command(game_id: int, steam_path=None) -> Popen:
    """Runs a game using the Steam browser protocol. The `steam_path` argument can be used to
    specify a specific path to the Steam executable instead of using the default Steam path.

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
    instead of using the default Steam path.
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
