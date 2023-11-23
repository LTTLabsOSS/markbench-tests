"""Dota 2 test script utils"""
from argparse import ArgumentParser
import win32api
import win32file
import winreg
import os
import logging
import re
import shutil
import pyautogui as gui
import pydirectinput as user
import sys
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

USERNAME = os.getlogin()
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def console_command(command):
    """Enter a console command"""
    for char in command:
        gui.press(char)
    user.press("enter")

def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()

def valid_filepath(path: str) -> bool:
    """Validate given path is valid and leads to an existing file. A directory
    will throw an error, path must be a file"""
    if path is None or len(path.strip()) <= 0:
        return False
    if os.path.isdir(path) is True:
        return False
    return os.path.isfile(path)

def get_local_drives() -> list[str]:
    """Returns a list containing letters from local drives"""
    drive_list = win32api.GetLogicalDriveStrings()
    drive_list = drive_list.split("\x00")[0:-1]  # the last element is ""
    list_local_drives = []
    for letter in drive_list:
        if win32file.GetDriveType(letter) == win32file.DRIVE_FIXED:
            list_local_drives.append(letter)
    return list_local_drives

def install_location() -> any:
    """Get installation location of Dota 2"""
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 570'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    #pylint: disable=undefined-variable
    except WindowsError:
        return None

def copy_replay() -> None:
    """Copy replay file to dota 2 folder"""
    replay_path = os.path.join(install_location(), "game\\dota\\replays")
    src_file = os.path.join(SCRIPT_DIRECTORY, "benchmark.dem")
    destination_file = os.path.join(replay_path, os.path.basename(src_file))
    if os.path.isfile(src_file) is not True:
        source = r"\\Labs\labs\03_ProcessingFiles\Dota2\benchmark.dem"
        root_dir = os.path.dirname(os.path.realpath(__file__))
        destination = os.path.join(root_dir, "benchmark.dem")
        shutil.copyfile(source, destination)
    if not os.path.isfile(src_file):
        raise Exception(f"Can't find intro: {src_file}")
    try:
        Path(replay_path).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error(
            "Could not create directory - likely due to non-directory file existing at path.")
        raise e
    logging.info("Copying: %s -> %s", src_file, destination_file)
    shutil.copy(src_file, destination_file)

def copy_config() -> None:
    """Copy benchmark config to dota 2 folder"""
    config_path = os.path.join(install_location(), "game\\dota\\cfg")
    src_file = os.path.join(SCRIPT_DIRECTORY, "benchmark.cfg")
    destination_file = os.path.join(config_path, os.path.basename(src_file))
    if os.path.isfile(src_file) is not True:
        source = r"\\Labs\labs\03_ProcessingFiles\Dota2\benchmark.cfg"
        root_dir = os.path.dirname(os.path.realpath(__file__))
        destination = os.path.join(root_dir, "benchmark.cfg")
        shutil.copyfile(source, destination)
    if not os.path.isfile(src_file):
        raise Exception(f"Can't find config: {src_file}")
    try:
        Path(config_path).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error(
            "Could not create directory - likely due to non-directory file existing at path.")
        raise e
    logging.info("Copying: %s -> %s", src_file, destination_file)
    shutil.copy(src_file, destination_file)

def get_resolution():
    """Get current resolution from settings file"""
    video_config = os.path.join(install_location(), "game\\dota\\cfg\\video.txt")
    height_pattern = re.compile(r"\"setting.defaultresheight\"		\"(\d+)\"")
    width_pattern = re.compile(r"\"setting.defaultres\"		\"(\d+)\"")
    cfg = f"{video_config}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
            if height != 0 and width !=0:
                return (height, width)
    return (height, width)
