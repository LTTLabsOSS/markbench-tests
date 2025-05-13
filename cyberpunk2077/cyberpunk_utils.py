"""Utility functions for Cyberpunk 2077 test script"""
from argparse import ArgumentParser
import os
import logging
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from harness_utils.steam import get_app_install_location

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_GAME_ID = 1091500
CYBERPUNK_INSTALL_DIR = get_app_install_location(STEAM_GAME_ID)


def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()


def copy_from_network_drive():
    """Copies mod file from network drive to harness folder"""
    src_path = Path(r"\\Labs\labs\03_ProcessingFiles\Cyberpunk 2077\basegame_no_intro_videos.archive")
    dest_path = SCRIPT_DIRECTORY / "basegame_no_intro_videos.archive"
    shutil.copyfile(src_path, dest_path)


def copy_no_intro_mod() -> None:
    """Copies no intro mod file"""
    try:
        mod_path = Path(f"{CYBERPUNK_INSTALL_DIR}\\archive\\pc\\mod")
        mod_path.mkdir(parents=True, exist_ok=True)

        src_path = SCRIPT_DIRECTORY / "basegame_no_intro_videos.archive"
        dest_path = mod_path / "basegame_no_intro_videos.archive"

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
        return
    except OSError:
        logging.error("Could not copy local mod file; Trying from network drive")
    try:
        copy_from_network_drive()

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
    except OSError as err:
        logging.error("Could not copy mod file from network drive")
        raise err


def read_current_resolution():
    """Get resolution from local game file"""
    app_data = os.getenv("LOCALAPPDATA")
    config_location = f"{app_data}\\CD Projekt Red\\Cyberpunk 2077"
    config_filename = "UserSettings.json"
    resolution_pattern = re.compile(r"\"value\"\: \"(\d+x\d+)\"\,")
    cfg = f"{config_location}\\{config_filename}"
    resolution = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = resolution_match.group(1)
    return resolution
