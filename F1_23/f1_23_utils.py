"""Utility functions supporting F1 23 test script."""
import os
import re
import winreg
import logging

def get_resolution() -> tuple[int]:
    """Gets resolution width and height from local xml file created by game."""
    username = os.getlogin()
    config_path = f"C:\\Users\\{username}\\Documents\\My Games\\F1 22\\hardwaresettings"
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
                height = height_match.group(2)
            if width_match is not None:
                width = width_match.group(1)
    return (width, height)


def remove_intro_videos(file_paths: list[str]) -> None:
    """Remove video files from paths to speed up game startup."""
    for video in file_paths:
        try:
            os.remove(video)
            logging.info("Removing video %s", video)
        except FileNotFoundError:
            # If file not found, it has likely already been deleted before.
            logging.info("Video already removed %s", video)


def f1_23_directory() -> any:
    """Gets the directory from the Windows Registry"""
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2108330'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


video_path = os.path.join(f1_23_directory(), "videos")

skippable = [
    os.path.join(video_path, "attract.bk2"),
    os.path.join(video_path, "cm_f1_sting.bk2")
]
