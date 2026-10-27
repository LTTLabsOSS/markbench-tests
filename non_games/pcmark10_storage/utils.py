"""UL PCMark 10 Storage test utils"""
from pathlib import Path
import psutil
import winreg
import re
import os
import sys
import win32api
import logging


PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.paths import harness_directories

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process
    return None

def regex_find_score_in_xml(result_regex: str):
    """Reads score from the fixed single-line result.xml file in the run directory"""
    xml_path = ARTIFACTS_DIRECTORY / "result.xml"

    if not xml_path.exists():
        logger.error("Result XML not found: %s", xml_path)
        return None

    try:
        text = xml_path.read_text(encoding="utf-8", errors="ignore").strip()
        match = re.search(result_regex, text)
        if match:
            return int(match.group(1))
        else:
            logger.error("Score not found in XML using regex: %s", result_regex)
            return None
    except Exception as e:
        logger.exception("Error reading XML file: %s", e)
        return None


def get_install_path() -> str:
    """Gets the path to the PCMark 10 installation directory from the registry key"""
    reg_path = r"Software\UL\PCMark 10"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, "InstallDir")
    return value


# need to fix this still
def find_pcmark10_version() -> str:
    """Gets the version of an executable located in the install path."""
    install_path = get_install_path()

    if not install_path:
        logger.info("Installation path not found.")
        return ""

    exe_path = os.path.join(install_path, "PCMark10Cmd.exe")

    if not os.path.exists(exe_path):
        logger.info("Executable not found at %s", exe_path)
        return ""

    try:
        # Get all file version info
        info = win32api.GetFileVersionInfo(exe_path, "\\")

        # Extract FileVersionMS and FileVersionLS
        ms = info.get("FileVersionMS")
        ls = info.get("FileVersionLS")

        if ms is None or ls is None:
            logger.info("No FileVersionMS or FileVersionLS found.")
            return ""

        # Convert to human-readable version: major.minor.build.revision
        major = ms >> 16
        minor = ms & 0xFFFF
        build = ls >> 16
        revision = ls & 0xFFFF

        version = f"{major}.{minor}.{build}.{revision}"
        return version

    except Exception as e:
        logger.info("Error retrieving version info from %s: %s", exe_path, e)
        return ""  # Return empty string if version info retrieval fails


#need to fix this still
def find_test_version() -> str:
    """Gets the version of an executable located in the chops path."""
    chops_path = "C:\\ProgramData\\UL\\PCMark 10\\chops\\dlc\\pcm10-storage-test\\x64"

    logger.info("The install path for the test is %s", chops_path)

    if not chops_path:
        logger.info("Installation path not found.")
        return ""

    exe_path = os.path.join(chops_path, "PCMark10-Storage.exe")

    if not os.path.exists(exe_path):
        logger.info("Executable 'PCMark10-Storage.exe' not found at %s", exe_path)
        return ""

    try:
        lang, codepage = win32api.GetFileVersionInfo(
            exe_path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return str(win32api.GetFileVersionInfo(exe_path, str_info_path))
    except Exception as e:
        logger.info("Error retrieving version info from %s: %s", exe_path, e)
        return ""  # Return empty string if version info retrieval fails
