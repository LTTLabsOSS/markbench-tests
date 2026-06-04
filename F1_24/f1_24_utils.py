"""Utility functions supporting F1 24 test script."""

import re
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.paths import user_documents

STEAM_GAME_ID = 2488620
CONFIG_FILENAME = "hardware_settings_config.xml"


def get_game_documents_dir() -> Path:
    """Returns the F1 24 Documents directory."""
    return user_documents(STEAM_GAME_ID) / "My Games" / "F1 24"


def get_config_file() -> Path:
    """Returns the F1 24 hardware settings config path."""
    return get_game_documents_dir() / "hardwaresettings" / CONFIG_FILENAME


def get_benchmark_results_path() -> Path:
    """Returns the F1 24 benchmark results directory."""
    return get_game_documents_dir() / "benchmark"


def get_resolution(config_file: Path | None = None) -> tuple[int, int]:
    """Gets resolution width and height from local xml file created by game."""
    resolution = re.compile(r"<resolution width=\"(\d+)\" height=\"(\d+)\"")
    cfg = config_file or get_config_file()
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
