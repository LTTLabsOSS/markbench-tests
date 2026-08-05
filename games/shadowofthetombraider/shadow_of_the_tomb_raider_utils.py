"""Utility functions for Shadow of the Tomb Raider test script"""

from pathlib import Path

from harness_utils.registry import read_registry_value

STEAM_GAME_ID = 750920
REGISTRY_PATH = r"SOFTWARE\Eidos Montreal\Shadow of the Tomb Raider\Graphics"


def get_reg(name):
    """Get registry key value"""
    return read_registry_value(REGISTRY_PATH, name, steam_app_id=STEAM_GAME_ID)


def get_resolution() -> tuple[int, int]:
    """Get resolution from registry"""
    width = get_reg("FullscreenWidth")
    height = get_reg("FullscreenHeight")
    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("Could not read resolution from the registry")
    return (height, width)


def get_latest_file_report(directory: Path) -> Path | None:
    """Get the latest benchmark report."""
    files = [
        file
        for file in directory.iterdir()
        if file.is_file() and file.suffix != ".log" and "frametimes" not in file.name
    ]
    return max(files, key=lambda path: path.stat().st_mtime, default=None)
