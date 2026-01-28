"""Utility functions supporting F1 24 test script."""

import os
import re
import sys
from pathlib import Path

HARNESS_UTILS_PARENT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(1, str(HARNESS_UTILS_PARENT))

from harness_utils.misc import remove_files
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import (
    exec_steam_run_command,
    get_app_install_location,
    get_build_id,
)

STEAM_GAME_ID = 2488620

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"


INTRO_VIDEOS_DIR = Path(get_app_install_location(STEAM_GAME_ID)) / "videos"
intro_videos = [
    os.path.join(INTRO_VIDEOS_DIR, "attract.bk2"),
    os.path.join(INTRO_VIDEOS_DIR, "cm_f1_sting.bk2"),
]


def start_game():
    exec_steam_run_command(STEAM_GAME_ID)


def find_latest_result_file(base_path):
    pattern = r"benchmark_.*\.xml"
    directory = Path(base_path)

    list_of_files = [
        p for p in directory.iterdir() if re.search(pattern, p.name, re.IGNORECASE)
    ]

    latest_file = max(list_of_files, key=lambda p: p.stat().st_mtime)

    return latest_file


def remove_intro_videos():
    remove_files(intro_videos)


def get_resolution() -> tuple[int, int]:
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
                height = int(height_match.group(2))
            if width_match is not None:
                width = int(width_match.group(1))
    return (width, height)


def write_report(log_dir: Path, start_time: int, end_time: int):
    width, height = get_resolution()

    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, report, "report.json")
