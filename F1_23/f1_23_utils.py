import os
import re
import winreg
import logging

# Stub
def get_resolution():    
    USERNAME = os.getlogin()
    CONFIG_LOCATION = f"C:\\Users\\{USERNAME}\\Documents\\My Games\\F1 23\\hardwaresettings"
    CONFIG_FILENAME = "hardware_settings_config.xml"
    resolution = re.compile(r"<resolution width=\"(\d+)\" height=\"(\d+)\"")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height = 0
    width = 0
    with open(cfg) as f:
        lines = f.readlines()
        for line in lines:
            height_match = resolution.search(line)
            width_match = resolution.search(line)
            if height_match is not None:
                height = height_match.group(2)
            if width_match is not None:
                width = width_match.group(1)
    return (width, height)

def remove_intro_videos(file_paths: list[str]) -> None:
    for video in file_paths:
        try:
            os.remove(video)
            logging.info(f"Removing video {video}")
        except FileNotFoundError:
            logging.info(f"Video already removed {video}")
            # If file not found, it has likely already been deleted before.
            pass
        

def F1_23_DIRECTORY() -> any:
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2108330'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


video_path = os.path.join(F1_23_DIRECTORY(), "videos")

skippable = [
    os.path.join(video_path, "attract.bk2"),
    os.path.join(video_path, "cm_f1_sting.bk2")
]