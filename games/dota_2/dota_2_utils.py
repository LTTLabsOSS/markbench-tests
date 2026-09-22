"""Dota 2 test script utils"""

import bz2
import logging
import re
import shutil
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.steam import (
    get_active_steam_account_id,
    get_app_install_location,
    get_steam_folder_path,
)

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 570
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_USER_ID = get_active_steam_account_id()

REPLAY_FILENAME = "8821954344_416769358.dem"
REPLAY_ARCHIVE_FILENAME = f"{REPLAY_FILENAME}.bz2"
REPLAY_PATH = SCRIPT_DIRECTORY / REPLAY_FILENAME
ARCHIVE_PATH = SCRIPT_DIRECTORY / REPLAY_ARCHIVE_FILENAME

DOWNLOAD_URL = (
    "http://replay272.valve.net/570/"
    f"{REPLAY_ARCHIVE_FILENAME}"
)

if sys.platform == "win32":
    DEFAULT_INSTALL_PATH = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta"
)   
    NETWORK_REPLAY_DIRECTORY = Path(
        r"\\labs.lmg.gg\labs\03\_ProcessingFiles\Dota2"
    )
else:
    DEFAULT_INSTALL_PATH = Path(
    "~/.steam/steam/steamapps/common/dota 2 beta"
    ).expanduser()
    NETWORK_REPLAY_DIRECTORY = Path(
        "/mnt/labs.lmg.gg/labs/03_ProcessingFiles/Dota2"
    )



def get_install_path():
    """Gets install path for DOTA 2"""
    install_path = get_app_install_location(STEAM_GAME_ID)
    if not install_path:
        return DEFAULT_INSTALL_PATH
    return install_path


def copy_replay_from_network_drive():
    """Copies replay file from network drive to harness folder"""
    src_path = NETWORK_REPLAY_DIRECTORY / REPLAY_FILENAME

    dest_path = REPLAY_PATH
    try:
        logger.info("Copying the replay from the network drive to the harness folder.")
        shutil.copyfile(src_path, dest_path)
    except OSError as err:
        logger.error("Network copy failed: %s", err)
        raise


def verify_replay() -> None:
    """Ensure the replay exists in SCRIPT_DIRECTORY."""
    src_path = REPLAY_PATH

    if src_path.exists():
        logger.info("The replay exists in the harness folder. Copying the files.")
        return

    logger.info("The replay file doesn't exist in the harness folder.")

    try:
        copy_replay_from_network_drive()
        logger.info("Replay copied successfully from network drive.")
        return
    except OSError as err:
        logger.warning(
            "Could not copy from the network drive. %s",
            err,
        )

    logger.info("Falling back to downloading replay from the internet.")
    download_replay()


def download_replay() -> None:
    """Download and extract the replay from Valve's website."""
    logger.info("Downloading the replay from %s", DOWNLOAD_URL)

    try:
        with urlopen(DOWNLOAD_URL, timeout=180) as response, ARCHIVE_PATH.open(
            "wb"
        ) as archive_file:
            shutil.copyfileobj(response, archive_file)

        logger.info("Extracting replay to %s", REPLAY_PATH)

        with bz2.open(ARCHIVE_PATH, "rb") as compressed_file, REPLAY_PATH.open(
            "wb"
        ) as replay_file:
            shutil.copyfileobj(compressed_file, replay_file)

        ARCHIVE_PATH.unlink()

    except (URLError, TimeoutError, OSError, EOFError) as error:
        raise RuntimeError(
            f"Failed to download or extract the replay: {error}"
        ) from error

    if not REPLAY_PATH.exists():
        raise RuntimeError(
            f"Replay extraction completed but {REPLAY_PATH} does not exist."
        )


def copy_replay() -> None:
    """Copy the replay"""
    replay_game_path = Path(get_install_path(), "game", "dota", "replays")
    replay_game_path.mkdir(parents=True, exist_ok=True)
    dest_path = replay_game_path / REPLAY_FILENAME

    # Try copying the benchmark to the correct area.
    try:
        logger.info("Copying: %s -> %s", REPLAY_PATH, dest_path)
        shutil.copyfile(REPLAY_PATH, dest_path)
    except OSError as err:
        logger.error("Could not copy the replay file: %s", err)
        raise


def copy_config() -> None:
    """Copy benchmark config to dota 2 folder"""
    try:
        config_path = Path(get_install_path(), "game", "dota", "cfg")
        config_path.mkdir(parents=True, exist_ok=True)

        files_to_copy = ["2026_benchmark_run.cfg", "benchmark_load.cfg"]

        for filename in files_to_copy:
            src_path = SCRIPT_DIRECTORY / filename
            dest_path = config_path / filename

            logger.info("Copying: %s -> %s", src_path, dest_path)
            shutil.copyfile(src_path, dest_path)
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
