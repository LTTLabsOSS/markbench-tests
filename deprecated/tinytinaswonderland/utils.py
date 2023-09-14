import win32api
import win32file
import winreg
import os
import logging
import re

EXECUTABLE = "Wonderlands.exe"


def get_documents_path() -> str:
    SHELL_FOLDER_KEY = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    try:
        root_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        shell_folders_handle = winreg.OpenKeyEx(root_handle, SHELL_FOLDER_KEY)
        personal_path_key = winreg.QueryValueEx(shell_folders_handle, 'Personal')
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
    for drive_letter in drives:
        try_me = f"{drive_letter}Program Files\\Epic Games\\TinyTinasWonderlands\\OakGame\\Binaries\\Win64\\{EXECUTABLE}"
        try_me2 = f"{drive_letter}Epic Games\\TinyTinasWonderlands\\OakGame\\Binaries\\Win64\\{EXECUTABLE}"
        if valid_filepath(try_me):
            return try_me
        if valid_filepath(try_me2):
            return try_me2
    raise ValueError("Cannot find the install path for the game!")


def read_resolution() -> tuple[int]:
    dest = f"{get_documents_path()}\\My Games\\Tiny Tina's Wonderlands\\Saved\\Config\\WindowsNoEditor\\GameUserSettings.ini"
    hpattern = re.compile(r"ResolutionSizeY=(\d*)")
    wpattern = re.compile(r"ResolutionSizeX=(\d*)")
    h = w = 0
    with open(dest) as fp:
        lines = fp.readlines()
        for line in lines:
            result = hpattern.match(line)
            if result is not None:
                h = result.group(1)

            result2 = wpattern.match(line)
            if result2 is not None:
                w = result2.group(1)
            if int(h) > 0 and int(w) > 0:
                break
    logging.info(f"Current resolution is {h}x{w}")
    return (h, w)
