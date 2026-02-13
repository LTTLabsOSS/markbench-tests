"""Utility functions for Shadow of the Tomb Raider test script"""
from argparse import ArgumentParser
import os
from pathlib import Path
import winreg


def get_reg(name) -> any:
    """Get registry key value"""
    reg_path = r'SOFTWARE\Eidos Montreal\Shadow of the Tomb Raider\Graphics'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except Exception:
        return None


def get_resolution() -> tuple[int]:
    """Get resolution from registry"""
    width = get_reg("FullscreenWidth")
    height = get_reg("FullscreenHeight")
    return (height, width)


def get_latest_file_report(directory: Path):
    """
    get latest benchmark report from SOTTR documents directory
    """
    # Get list of all items in the directory with full paths
    entries = (os.path.join(directory, fn) for fn in os.listdir(directory))
    # Filter out directories, keep only files
    files = [
        file for file in entries
        if os.path.isfile(file) and not file.endswith('.log') and "frametimes" not in file
    ]
    if not files:
        return None  # No files found
    # Get the file with the latest modification time
    latest_file = max(files, key=os.path.getmtime)
    return latest_file
    