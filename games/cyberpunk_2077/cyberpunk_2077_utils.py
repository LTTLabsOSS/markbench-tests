"""Utility functions for Cyberpunk 2077 test script"""

import logging
import re
import shutil
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)
from harness_utils.paths import game_install_path, local_appdata, network_drive_path

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_GAME_ID = 1091500
NO_INTRO_MOD_FILENAME = "basegame_no_intro_videos.archive"


def copy_from_network_drive() -> Path:
    """Copies no intro mod file from network drive to harness folder."""
    src_path = (
        network_drive_path()
        / "03_ProcessingFiles"
        / "Cyberpunk 2077"
        / NO_INTRO_MOD_FILENAME
    )
    dest_path = SCRIPT_DIRECTORY / NO_INTRO_MOD_FILENAME

    logger.info("Copying Cyberpunk no intro mod source: %s -> %s", src_path, dest_path)
    shutil.copyfile(src_path, dest_path)
    return dest_path


def copy_no_intro_mod() -> None:
    """Copies no intro mod file"""
    logger.info("Preparing Cyberpunk no intro mod copy")
    mod_path = game_install_path(STEAM_GAME_ID) / "archive" / "pc" / "mod"
    logger.info("Ensuring Cyberpunk mod directory exists path=%s", mod_path)
    mod_path.mkdir(parents=True, exist_ok=True)

    src_path = SCRIPT_DIRECTORY / NO_INTRO_MOD_FILENAME
    if not src_path.exists():
        src_path = copy_from_network_drive()

    dest_path = mod_path / NO_INTRO_MOD_FILENAME

    logger.info("Copying Cyberpunk no intro mod: %s -> %s", src_path, dest_path)
    if src_path.resolve() != dest_path.resolve():
        shutil.copy(src_path, dest_path)
    else:
        logger.info("Cyberpunk no intro mod already at destination path=%s", dest_path)


def read_current_resolution():
    """Get resolution from local game file"""
    logger.info("Reading Cyberpunk current resolution")
    config_path = (
        local_appdata(STEAM_GAME_ID)
        / "CD Projekt Red"
        / "Cyberpunk 2077"
        / "UserSettings.json"
    )
    if not config_path.exists():
        raise RuntimeError(f"Missing path: {config_path}")
    logger.info("Reading Cyberpunk settings file path=%s", config_path)
    resolution_pattern = re.compile(r"\"value\"\: \"(\d+x\d+)\"\,")
    resolution = 0
    with open(config_path, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = resolution_match.group(1)
                logger.info("Found Cyberpunk current resolution=%s", resolution)
    return resolution
