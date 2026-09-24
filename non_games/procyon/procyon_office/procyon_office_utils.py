"""UL Procyon Office Productivity test utils"""

import logging
import re
import winreg
from pathlib import Path

import win32api

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
ARTIFACTS_DIRECTORY = SCRIPT_DIRECTORY / "run" / "artifacts"


def regex_find_score_in_xml(result_regex: str) -> str | None:
    """Reads a score from the Procyon result XML."""
    score_pattern = re.compile(result_regex)
    xml = ARTIFACTS_DIRECTORY / "result.xml"

    with open(xml, encoding="utf-8") as file:
        for line in file:
            score_match = score_pattern.search(line)
            if score_match is not None:
                return score_match.group(1)

    return None


def get_install_path() -> str:
    """Gets the path to the Procyon installation directory from the Procyon registry key"""
    reg_path = r"Software\UL\Procyon"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(reg_key, "InstallDir")
    return value


def find_procyon_version() -> str | None:
    """Gets the version of ProcyonCmd.exe."""

    install_path = get_install_path()

    if not install_path:
        logger.info("Installation path not found.")
        return None

    exe_path = Path(install_path) / "ProcyonCmd.exe"

    if not exe_path.exists():
        logger.info("Executable not found at %s", exe_path)
        return None

    try:
        info = win32api.GetFileVersionInfo(str(exe_path), "\\")

        ms = info.get("FileVersionMS")
        ls = info.get("FileVersionLS")

        if ms is None or ls is None:
            logger.info("No FileVersionMS or FileVersionLS found.")
            return None

        major = ms >> 16
        minor = ms & 0xFFFF
        build = ls >> 16
        revision = ls & 0xFFFF

        return f"{major}.{minor}.{build}.{revision}"

    except Exception as e:
        logger.info(
            "Error retrieving version info from %s: %s",
            exe_path,
            e,
        )
        return None


def find_test_version() -> str | None:
    """Gets the version of the Office Productivity benchmark executable."""

    chops_path = Path(r"C:\ProgramData\UL\Procyon\chops\dlc")

    exe_path = (
        chops_path
        / "officeproductivity-starter-test"
        / "OfficeProductivity-Starter.exe"
    )

    if not exe_path.exists():
        logger.info("Executable not found at %s", exe_path)
        return None

    try:
        lang, codepage = win32api.GetFileVersionInfo(
            str(exe_path),
            r"\VarFileInfo\Translation",
        )[0]

        str_info_path = (
            rf"\StringFileInfo\{lang:04X}{codepage:04X}\ProductVersion"
        )

        return win32api.GetFileVersionInfo(
            str(exe_path),
            str_info_path,
        )

    except Exception as e:
        logger.info(
            "Error retrieving version info from %s: %s",
            exe_path,
            e,
        )
        return None
