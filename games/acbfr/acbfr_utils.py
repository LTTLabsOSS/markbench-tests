"""Utility functions for Assassins Creed Black Flag Resynced test script"""

import logging
import re
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)
from harness_utils.paths import user_documents

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_GAME_ID = 3751950

def get_resolution():
    """Get current resolution from settings file"""
    config_path = (
        user_documents(STEAM_GAME_ID)
        / "Assassin's Creed Black Flag Resynced"
        / "ACBlackFlag.ini"
        )
    if not config_path.exists():
        raise RuntimeError(f"Missing path: {config_path}")
    logger.info("Reading AC Black Flag Resynced settings file path=%s", config_path)
    height_pattern = re.compile(r"FullscreenHeight=(\d+)")
    width_pattern = re.compile(r"FullscreenWidth=(\d+)")
    height = None
    width = None
    with open(config_path, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = int(height_match.group(1))
            if width_match is not None:
                width = int(width_match.group(1))
            if height is not None and width is not None:
                return (width, height)
    return (width, height)
