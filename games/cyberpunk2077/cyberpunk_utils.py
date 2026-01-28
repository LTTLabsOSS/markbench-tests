"""Utility functions for Cyberpunk 2077 test script"""

import logging
import os
import re
import shutil
import sys
from pathlib import Path

HARNESSES_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(1, str(HARNESSES_ROOT))

from harness_utils.output import seconds_to_milliseconds, write_report_json
from harness_utils.steam import exec_steam_game, get_app_install_location, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_GAME_ID = 1091500
CYBERPUNK_INSTALL_DIR = get_app_install_location(STEAM_GAME_ID)


def copy_no_intro_mod() -> None:
    """Copies no intro mod file"""
    try:
        mod_path = Path(f"{CYBERPUNK_INSTALL_DIR}\\archive\\pc\\mod")
        mod_path.mkdir(parents=True, exist_ok=True)

        src_path = Path(
            r"\\labs.lmg.gg\labs\03_ProcessingFiles\Cyberpunk 2077\basegame_no_intro_videos.archive"
        )
        dest_path = mod_path / "basegame_no_intro_videos.archive"

        if dest_path.exists():
            logging.info("No intro mod already exists")
        else:
            shutil.copyfile(src_path, dest_path)

        return
    except OSError:
        logging.error("could not copy mod file")


def start_game():
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(
        STEAM_GAME_ID, game_params=["--launcher-skip", "-skipStartScreen"]
    )


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


def write_report(log_directory: Path, start_time: int, end_time: int):
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }
    write_report_json(log_directory, report)
