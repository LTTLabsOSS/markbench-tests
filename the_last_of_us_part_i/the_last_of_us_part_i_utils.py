"""Utility functions for The Last of Us Part I test script"""
from argparse import ArgumentParser
import ctypes
import re
import os
import sys
import shutil
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.steam import get_registry_active_user

USERFOLDER = os.environ["USERPROFILE"]
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
TLOU_SAVE = SCRIPT_DIRECTORY.joinpath("SAVEFILE0A")

def get_args() -> any:
    """Get command line arg values"""
    parser = ArgumentParser()
    parser.add_argument(
        "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True)
    parser.add_argument(
        "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True)
    return parser.parse_args()


def get_windowed_resolution(lines: list[str]):
    """Get windowed resolution value from local game file"""
    width_pattern = re.compile(r"WindowWidth=(\d+)")
    height_pattern = re.compile(r"WindowHeight=(\d+)")

    window_width = 0
    window_height = 0

    for line in lines:
        width_match = width_pattern.search(line)
        height_match = height_pattern.search(line)

        if width_match:
            window_width = width_match.group(1)

        if height_match:
            window_height = height_match.group(1)

    return window_height, window_width


def get_borderless_resolution(lines: list[str]):
    """Get borderless resolution value from local game file

    Note:
    If resolution is set to native resolution, then the values of
    BorderlessWidth and BorderlessHeight saved in the config are 0, 0.
    Without getting into various 3rd-party gui libraries, we can grab
    resolution sizes from the system metrics if we get values of 0.
    However, this has limitations: This can only get values for the primary monitor
    and reportedly may not return correct values with high DPI displays.
    """

    width_pattern = re.compile(r"BorderlessWidth=(\d+)")
    height_pattern = re.compile(r"BorderlessHeight=(\d+)")

    window_width = 0
    window_height = 0

    user32 = ctypes.windll.user32

    for line in lines:
        width_match = width_pattern.search(line)
        height_match = height_pattern.search(line)

        if width_match:
            window_width = width_match.group(1)
            if window_width == 0:
                window_width = user32.GetSystemMetrics(0)

        if height_match:
            window_height = height_match.group(1)
            if window_height == 0:
                window_height = user32.GetSystemMetrics(1)

    return window_height, window_width


def get_resolution(config_path: str):
    """Gets the resolution by retrieving the active steam user id from
    registry to complete the path to the local config file.
    Then parses the local config file and grabbing values depending on
    if the display settings were set to Windowed or Borderless windowed mode.
    """
    window_mode_pattern = re.compile(r"WindowMode=(\d)")

    window_mode = None
    window_width = 0
    window_height = 0

    with open(config_path, encoding="utf-8") as file:
        window_mode_line = file.readline()
        window_mode = window_mode_pattern.search(window_mode_line).group(1)

        if not window_mode:
            return window_height, window_width

        lines = file.readlines()
        if int(window_mode) == 1:
            window_height, window_width = get_borderless_resolution(lines)
        else:
            window_height, window_width = get_windowed_resolution(lines)

    return window_height, window_width


def copy_autosave():
    """
    Copies The Last of Us Part I autosave folder to the savedata directory.
    Existing destination is replaced.
    """
    src_autosave_dir = Path(TLOU_SAVE)
    steam_user_id = str(get_registry_active_user())
    dest_savedata_dir = Path(
    USERFOLDER,
    "Saved Games",
    "The Last of Us Part I",
    "users",
    steam_user_id,
    "SaveData",
)

    if not src_autosave_dir.exists():
        raise FileNotFoundError(f"Source autosave folder not found: {src_autosave_dir}")

    # Ensure parent directory exists
    dest_savedata_dir.mkdir(parents=True, exist_ok=True)

    dest_folder = dest_savedata_dir.joinpath(TLOU_SAVE.name)
    # Remove existing savedata (autosave restore should be exact)
    if dest_folder.exists():
        shutil.rmtree(dest_folder)

    shutil.copytree(src_autosave_dir, dest_folder)

    print(f"Autosave copied from {src_autosave_dir} -> {dest_folder}")