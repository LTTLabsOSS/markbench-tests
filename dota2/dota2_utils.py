"""Dota 2 test script utils"""
from argparse import ArgumentParser
import logging
import re
import shutil
import sys
from pathlib import Path

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.steam import get_app_install_location, get_registry_active_user, get_steam_folder_path

STEAM_GAME_ID = 570
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_USER_ID = get_registry_active_user()
DEFAULT_INSTALL_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta")


def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()


def get_install_path():
    """Gets install path for DOTA 2"""
    install_path = get_app_install_location(STEAM_GAME_ID)
    if not install_path:
        return DEFAULT_INSTALL_PATH
    return install_path


def copy_replay_from_network_drive():
    """Copies replay file from network drive to harness folder"""
    src_path = Path(r"\\Labs\labs\03_ProcessingFiles\Dota2\benchmark.dem")
    dest_path = SCRIPT_DIRECTORY / "benchmark.dem"
    shutil.copyfile(src_path, dest_path)


def copy_replay() -> None:
    """Copy replay file to dota 2 folder"""
    try:
        replay_path = Path(get_install_path(), "game\\dota\\replays")
        replay_path.mkdir(parents=True, exist_ok=True)

        src_path = SCRIPT_DIRECTORY / "benchmark.dem"
        dest_path = replay_path / "benchmark.dem"

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
        return
    except OSError:
        logging.error("Could not copy local replay file; Trying from network drive.")
    try:
        copy_replay_from_network_drive()

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
    except OSError as err:
        logging.error("Could not copy replay file.")
        raise err


def copy_config() -> None:
    """Copy benchmark config to dota 2 folder"""
    try:
        config_path = Path(get_install_path(), "game\\dota\\cfg")
        config_path.mkdir(parents=True, exist_ok=True)

        src_path = SCRIPT_DIRECTORY / "benchmark.cfg"
        dest_path = config_path / "benchmark.cfg"

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
    except OSError as err:
        logging.error("Could not copy config file.")
        raise err


def read_config() -> list[str] | None:
    """Looks for config file and returns contents if found"""
    userdata_path = Path(get_steam_folder_path(), "userdata", str(STEAM_USER_ID), str(STEAM_GAME_ID), "local", "cfg", "video.txt")
    install_path = Path(get_install_path(), "game", "dota", "cfg", "video.txt")
    try:
        with open(userdata_path, encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        logging.error("Did not find config file at path %s. Trying path %s", userdata_path, install_path)
    try:
        with open(install_path, encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        logging.error("Did not find config file at path %s", install_path)
    return None


def get_resolution():
    """Get current resolution from settings file"""
    height_pattern = re.compile(r"\"setting.defaultresheight\"		\"(\d+)\"")
    width_pattern = re.compile(r"\"setting.defaultres\"		\"(\d+)\"")
    height = 0
    width = 0
    lines = read_config()

    if lines is None:
        logging.error("Could not find the video config file.")
        return (height, width)

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
