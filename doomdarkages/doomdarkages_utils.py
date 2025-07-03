"""Utility functions supporting F1 24 test script."""
import os
import re
from pathlib import Path
import logging
import shutil

from harness_utils.steam import get_app_install_location
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
STEAM_GAME_ID = 3017860


def get_resolution() -> tuple[int]:
    """Gets resolution width and height from local xml file created by game."""
    username = os.getlogin()
    config_path = f"C:\\Users\\{username}\\Documents\\My Games\\F1 24\\hardwaresettings"
    config_filename = "hardware_settings_config.xml"
    resolution = re.compile(r"<resolution width=\"(\d+)\" height=\"(\d+)\"")
    cfg = f"{config_path}\\{config_filename}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = resolution.search(line)
            width_match = resolution.search(line)
            if height_match is not None:
                height = height_match.group(2)
            if width_match is not None:
                width = width_match.group(1)
    return (width, height)

def copy_launcher_config() -> None:
    """Copy benchmark config to dota 2 folder"""
    try:
        LAUNCHERCONFIG_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "launcherData", "base", "configs")
        LAUNCHERCONFIG_PATH.mkdir(parents=True, exist_ok=True)

        src_path = SCRIPT_DIRECTORY / "launcher.cfg"
        dest_path = LAUNCHERCONFIG_PATH / "launcher.cfg"

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
    except OSError as err:
        logging.error("Could not copy config file.")
        raise err