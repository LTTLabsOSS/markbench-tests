"""UL Procyon AI Image Generation test utils"""

import logging
import re
import winreg
from pathlib import Path

import psutil
import win32api

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
ARTIFACTS_DIRECTORY = SCRIPT_DIRECTORY / "run" / "artifacts"


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] == process_name:
            return process
    return None


def find_score_in_xml():
    """Reads a score from the Procyon result XML."""
    score_pattern = re.compile(r"<AIImageGenerationOverallScore>(\d+)")
    xml = ARTIFACTS_DIRECTORY / "result.xml"
    score_value = None
    with open(xml, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            score_match = score_pattern.search(line)
            if score_match is not None:
                score_value = score_match.group(1)
    return score_value


def get_install_path() -> str:
    """Gets the path to the Procyon installation directory from the Procyon registry key"""
    reg_path = r"Software\UL\Procyon"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, "InstallDir")
    return value


def find_procyon_versions(log_path: Path) -> tuple[str | None, str | None]:
    """Gets the Procyon Client and Product versions from the Procyon log."""
    if not log_path.exists():
        return None, None

    log = log_path.read_text(encoding="utf-8")

    match = re.search(
        r"Procyon Command Line Client version:\s*"
        r"(\d+\.\d+\.\d+)\s+\d+,\s*"
        r"Product version:\s*"
        r"(\d+\.\d+\.\d+)\s+\d+",
        log,
        re.IGNORECASE,
    )

    if match is None:
        return None, None

    return match.group(1), match.group(2)


def find_test_version() -> str | None:
    """Gets the version of an executable located in the chops path."""
    chops_path = Path(
        r"C:\ProgramData\UL\Procyon\chops\dlc\ai-imagegeneration-benchmark"
    )

    logger.info("The install path for the test is %s", chops_path)

    if not chops_path:
        logger.info("Installation path not found.")
        return None
    
    exe_path = (
        chops_path
        / "Handler.exe"
    )

    if not exe_path.exists():
        logger.info("Executable 'Handler.exe' not found at %s", exe_path)
        return None

    try:
        lang, codepage = win32api.GetFileVersionInfo(
            str(exe_path), "\\VarFileInfo\\Translation"
        )[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(str(exe_path), str_info_path)
    except Exception as e:
        logger.info("Error retrieving version info from %s: %s", exe_path, e)
        return None  # Return None if version info retrieval fails

def check_procyon_run_status(log_path):
    """Fail if Procyon reports that the run ended with an error."""
    log = log_path.read_text(encoding="utf-8")
    return "The status of the run was Error" not in log
