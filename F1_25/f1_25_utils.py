"""Utility functions supporting F1 25 test script."""

import re
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.paths import user_documents

STEAM_GAME_ID = 3059520


def get_resolution() -> tuple[int, int]:
    """Gets resolution width and height from local XML file created by game."""
    cfg = (
        user_documents(STEAM_GAME_ID)
        / "My Games"
        / "F1 25"
        / "hardwaresettings"
        / "hardware_settings_config.xml"
    )
    resolution = re.compile(r'<resolution width="(\d+)" height="(\d+)"')
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            match = resolution.search(line)
            if match is not None:
                width = int(match.group(1))
                height = int(match.group(2))
    return (width, height)
