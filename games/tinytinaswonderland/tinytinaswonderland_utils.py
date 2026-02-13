"""tiny tina's wonderlands utils"""
import winreg
import os
import logging
import re

EXECUTABLE = "Wonderlands.exe"

def find_latest_result_file(base_path):
    """Look for files in the benchmark results path that match the pattern in the regular expression"""
    pattern = r"BenchmarkData.*\.txt"
    list_of_files = []
    for filename in os.listdir(base_path):
        if re.search(pattern, filename, re.IGNORECASE):
            list_of_files.append(base_path + '\\' +filename)
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file


def get_documents_path() -> str:
    """get my documents path"""
    shell_folder_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    try:
        root_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        shell_folders_handle = winreg.OpenKeyEx(root_handle, shell_folder_key)
        personal_path_key = winreg.QueryValueEx(shell_folders_handle, 'Personal')
        return personal_path_key[0]
    finally:
        root_handle.Close()


def read_resolution() -> tuple[int]:
    """read current resolution"""
    dest = f"{get_documents_path()}\\My Games\\Tiny Tina's Wonderlands\\Saved\\Config\\WindowsNoEditor\\GameUserSettings.ini"
    hpattern = re.compile(r"ResolutionSizeY=(\d*)")
    wpattern = re.compile(r"ResolutionSizeX=(\d*)")
    h = w = 0
    with open(dest, encoding="utf-8") as fp:
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
    logging.info("Current resolution is %dx%d", w, h)
    return (h, w)
