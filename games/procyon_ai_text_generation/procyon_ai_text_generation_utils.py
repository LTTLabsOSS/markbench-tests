"""UL Procyon AI Text Generation test utils"""
from pathlib import Path
import psutil
import winreg
import re
import os
import win32api
import logging

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process
    return None


def regex_find_score_in_xml(result_regex):
    """Reads score from local game log"""
    score_pattern = re.compile(result_regex)
    cfg = f"{LOG_DIR}\\result.xml"
    score_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            score_match = score_pattern.search(line)
            if score_match is not None:
                score_value = score_match.group(1)
    return score_value


def get_install_path() -> str:
    """Gets the path to the Steam installation directory from the SteamPath registry key"""
    reg_path = r"Software\UL\Procyon"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, "InstallDir")
    return value


def find_procyon_version() -> str:
    """Gets the version of an executable located in the install path."""
    install_path = get_install_path()

    if not install_path:
        logging.info("Installation path not found.")
        return ""

    exe_path = os.path.join(install_path, "ProcyonCmd.exe")

    if not os.path.exists(exe_path):
        logging.info("Executable not found at %s", exe_path)
        return ""

    try:
        # Get all file version info
        info = win32api.GetFileVersionInfo(exe_path, "\\")

        # Extract FileVersionMS and FileVersionLS
        ms = info.get("FileVersionMS")
        ls = info.get("FileVersionLS")

        if ms is None or ls is None:
            logging.info("No FileVersionMS or FileVersionLS found.")
            return ""

        # Convert to human-readable version: major.minor.build.revision
        major = ms >> 16
        minor = ms & 0xFFFF
        build = ls >> 16
        revision = ls & 0xFFFF

        version = f"{major}.{minor}.{build}.{revision}"
        return version

    except Exception as e:
        logging.info("Error retrieving version info from %s: %s", exe_path, e)
        return ""  # Return empty string if version info retrieval fails


def find_test_version() -> str:
    """Gets the version of an executable located in the chops path."""
    chops_path = "C:\\ProgramData\\UL\\Procyon\\chops\\dlc\\ai-textgeneration-benchmark\\x64"

    logging.info("The install path for the test is %s", chops_path)

    if not chops_path:
        logging.info("Installation path not found.")
        return ""

    exe_path = os.path.join(chops_path, "Handler.exe")

    if not os.path.exists(exe_path):
        logging.info("Executable 'Handler.exe' not found at %s", exe_path)
        return ""

    try:
        lang, codepage = win32api.GetFileVersionInfo(
            exe_path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return str(win32api.GetFileVersionInfo(exe_path, str_info_path))
    except Exception as e:
        logging.info("Error retrieving version info from %s: %s", exe_path, e)
        return ""  # Return empty string if version info retrieval fails
