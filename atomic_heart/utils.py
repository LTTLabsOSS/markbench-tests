"""Atomic Heart utility functions"""
import os
import sys
import re
import winreg
import logging
import pydirectinput as user

sys.path.insert(1, os.path.join(sys.path[0], '..'))

APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\AtomicHeart\\Saved\\Config\\WindowsNoEditor"
CONFIG_FILENAME = "GameUserSettings.ini"
PROCESS_NAME = "AtomicHeart"

def get_install_location() -> any:
    """Gets install location based on registry"""
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 668580'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

video_path = os.path.join(get_install_location(), "AtomicHeart\\Content\\Movies")

skippable = [
    os.path.join(video_path, "Launch_4k_60FPS_PS5.mp4"),
    os.path.join(video_path, "Launch_4k_60FPS_XboxXS.mp4"),
    os.path.join(video_path, "Launch_FHD_30FPS_PS4.mp4"),
    os.path.join(video_path, "Launch_FHD_30FPS_XboxOne.mp4"),
    os.path.join(video_path, "Launch_FHD_60FPS_PC_Steam.mp4")
]

user.FAILSAFE = False

def remove_intros(file_paths: list[str]) -> None:
    """Removes files from given paths"""
    for video in file_paths:
        try:
            os.remove(video)
            logging.info("Removing video %s", video)
        except FileNotFoundError:
            logging.info("Video already removed %s", video)
            # If file not found, it has likely already been deleted before.


def read_resolution():
    """Gets resolution width and height values from local file"""
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)
