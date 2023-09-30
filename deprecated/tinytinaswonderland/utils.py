"""Utility functions for Tiny Tina's Wonderland test script"""
import logging
import os
import re
import winreg

import cv2
import win32api
import win32file

EXECUTABLE = "Wonderlands.exe"


def get_documents_path() -> str:
    """Use registry to find documents path"""
    shell_folder_key = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    )
    try:
        root_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        shell_folders_handle = winreg.OpenKeyEx(root_handle, shell_folder_key)
        personal_path_key = winreg.QueryValueEx(shell_folders_handle, "Personal")
        return personal_path_key[0]
    finally:
        root_handle.Close()


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


def try_install_paths(drives) -> str:
    """Look for executable in common install paths"""
    for drive_letter in drives:
        try_me = (
            f"{drive_letter}Program Files\\Epic Games\\TinyTinasWonderlands"
            f"\\OakGame\\Binaries\\Win64\\{EXECUTABLE}"
        )
        try_me2 = (
            f"{drive_letter}Epic Games\\TinyTinasWonderlands"
            f"\\OakGame\\Binaries\\Win64\\{EXECUTABLE}"
        )
        if valid_filepath(try_me):
            return try_me
        if valid_filepath(try_me2):
            return try_me2
    raise ValueError("Cannot find the install path for the game!")


def read_resolution() -> tuple[int]:
    """Read resolution from local ini file"""
    dest = (
        f"{get_documents_path()}\\My Games\\Tiny Tina's Wonderlands"
        "\\Saved\\Config\\WindowsNoEditor\\GameUserSettings.ini"
    )
    hpattern = re.compile(r"ResolutionSizeY=(\d*)")
    wpattern = re.compile(r"ResolutionSizeX=(\d*)")
    h = w = 0
    with open(dest, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            result = hpattern.match(line)
            if result is not None:
                h = result.group(1)

            result2 = wpattern.match(line)
            if result2 is not None:
                w = result2.group(1)
            if int(h) > 0 and int(w) > 0:
                break
    logging.info("Current resolution is %dx%d", h, w)
    return (h, w)


# path relative to script
script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
dir16x9 = os.path.join(images_dir, "16x9")
dir16x10 = os.path.join(images_dir, "16x10")

templates = {
    "options": {
        "16x10": cv2.imread(
            os.path.join(dir16x10, "options.png"), cv2.IMREAD_UNCHANGED
        ),
        "16x9": cv2.imread(os.path.join(dir16x9, "options.png"), cv2.IMREAD_UNCHANGED),
    },
    "benchmark": {
        "16x10": cv2.imread(
            os.path.join(dir16x10, "benchmark.png"), cv2.IMREAD_UNCHANGED
        ),
        "16x9": cv2.imread(
            os.path.join(dir16x9, "benchmark.png"), cv2.IMREAD_UNCHANGED
        ),
    },
    "start": {
        "16x10": cv2.imread(os.path.join(dir16x10, "start.png"), cv2.IMREAD_UNCHANGED),
        "16x9": cv2.imread(os.path.join(dir16x9, "start.png"), cv2.IMREAD_UNCHANGED),
    },
}
