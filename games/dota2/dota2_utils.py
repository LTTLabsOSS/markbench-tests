"""Dota 2 test script utils"""

import logging
import re
import shutil
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.steam import (
    get_app_install_location,
    get_active_steam_account_id,
    get_steam_folder_path,
)

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 570
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_USER_ID = get_active_steam_account_id()
DEFAULT_INSTALL_PATH = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta"
)


def get_install_path():
    """Gets install path for DOTA 2"""
    install_path = get_app_install_location(STEAM_GAME_ID)
    if not install_path:
        return DEFAULT_INSTALL_PATH
    return install_path


def copy_replay_from_network_drive():
    """Copies replay file from network drive to harness folder"""
    src_path = Path(r"\\labs.lmg.gg\labs\03_ProcessingFiles\Dota2\benchmark.dem")
    dest_path = SCRIPT_DIRECTORY / "benchmark.dem"
    try:
        logger.info("Copying the replay from the network drive to the harness folder.")
        shutil.copyfile(src_path, dest_path)
    except OSError as err:
        logger.error("Network copy failed: %s", err)
        raise


def verify_replay() -> None:
    """Ensure the replay exists in SCRIPT_DIRECTORY."""
    src_path = SCRIPT_DIRECTORY / "benchmark.dem"

    if src_path.exists():
        logger.info("The replay exists in the harness folder. Copying the files.")
        return

    logger.info("The replay file doesn't exist in the harness folder.")
    copy_replay_from_network_drive()


def copy_replay() -> None:
    """Copyihg the replay"""
    replay_path = Path(get_install_path(), "game\\dota\\replays")
    replay_path.mkdir(parents=True, exist_ok=True)

    src_path = SCRIPT_DIRECTORY / "benchmark.dem"
    dest_path = replay_path / "benchmark.dem"

    # Try copying the benchmark to the correct area.
    try:
        logger.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
        return
    except OSError as err:
        logger.error("Could not copy copy the replay file: %s", err)
        raise


def copy_config() -> None:
    """Copy benchmark config to dota 2 folder"""
    try:
        config_path = Path(get_install_path(), "game\\dota\\cfg")
        config_path.mkdir(parents=True, exist_ok=True)

        files_to_copy = ["benchmark_run.cfg", "benchmark_load.cfg"]

        for filename in files_to_copy:
            src_path = SCRIPT_DIRECTORY / filename
            dest_path = config_path / filename

            logger.info("Copying: %s -> %s", src_path, dest_path)
            shutil.copy(src_path, dest_path)
    except OSError as err:
        logger.error("Could not copy config files: %s", err)
        raise


def read_config() -> list[str] | None:
    """Looks for config file and returns contents if found"""
    userdata_path = Path(
        get_steam_folder_path(),
        "userdata",
        str(STEAM_USER_ID),
        str(STEAM_GAME_ID),
        "local",
        "cfg",
        "video.txt",
    )
    install_path = Path(get_install_path(), "game", "dota", "cfg", "video.txt")
    try:
        with open(userdata_path, encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        logger.error(
            "Did not find config file at path %s. Trying path %s",
            userdata_path,
            install_path,
        )
    try:
        with open(install_path, encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        logger.error("Did not find config file at path %s", install_path)
    return None


def get_resolution():
    """Get current resolution from settings file"""
    height_pattern = re.compile(r"\"setting.defaultresheight\"		\"(\d+)\"")
    width_pattern = re.compile(r"\"setting.defaultres\"		\"(\d+)\"")
    height = 0
    width = 0
    lines = read_config()

    if lines is None:
        logger.error("Could not find the video config file.")
        return (height, width)

    for line in lines:
        height_match = height_pattern.search(line)
        width_match = width_pattern.search(line)
        if height_match is not None:
            height = height_match.group(1)
        if width_match is not None:
            width = width_match.group(1)
        if height != 0 and width != 0:
            return (height, width)
    return (height, width)
