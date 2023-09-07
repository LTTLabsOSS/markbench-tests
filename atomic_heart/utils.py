import os
import pydirectinput as user
import sys
import re
import winreg
import logging

sys.path.insert(1, os.path.join(sys.path[0], '..'))

APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\AtomicHeart\\Saved\\Config\\WindowsNoEditor"
CONFIG_FILENAME = "GameUserSettings.ini"
PROCESS_NAME = "AtomicHeart"

def InstallLocation() -> any:
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 668580'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

video_path = os.path.join(InstallLocation(), "AtomicHeart\\Content\\Movies")

skippable = [
    os.path.join(video_path, "Launch_4k_60FPS_PS5.mp4"),
    os.path.join(video_path, "Launch_4k_60FPS_XboxXS.mp4"),
    os.path.join(video_path, "Launch_FHD_30FPS_PS4.mp4"),
    os.path.join(video_path, "Launch_FHD_30FPS_XboxOne.mp4"),
    os.path.join(video_path, "Launch_FHD_60FPS_PC_Steam.mp4")
]

user.FAILSAFE = False

def remove_intros(file_paths: list[str]) -> None:
    for video in file_paths:
        try:
            os.remove(video)
            logging.info(f"Removing video {video}")
        except FileNotFoundError:
            logging.info(f"Video already removed {video}")
            # If file not found, it has likely already been deleted before.
            pass


def read_resolution():
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height = 0
    width = 0
    with open(cfg) as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)


