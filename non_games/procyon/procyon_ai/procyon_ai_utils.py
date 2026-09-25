"""UL Procyon Computer Vision test utils"""

import logging
import os
import re
import sys
import winreg
from argparse import ArgumentParser
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
    """Reads score from local game log"""
    score_pattern = re.compile(r"<AIOverallScore>(\d+)")
    cfg = ARTIFACTS_DIRECTORY / "result.xml"
    score_value = 0
    with open(cfg, encoding="utf-8") as file:
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


def find_test_version() -> str:
    """Gets the version of an executable located in the chops path."""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine",
        dest="engine",
        help="The engine used to run the AI CV",
        required=True,
    )
    args = parser.parse_args()
    apps = [
        "AMD_CPU",
        "AMD_GPU0",
        "AMD_GPU1",
        "Intel_CPU",
        "Intel_GPU0",
        "Intel_GPU1",
        "Intel_NPU",
        "NVIDIA_GPU",
        "Qualcomm_HTP",
    ]

    if args.engine is None or args.engine not in apps:
        logger.info("unrecognized option for program")
        sys.exit(1)

    engine_config = {
        "AMD_CPU": ("aibenchmark-winml-test", "WinML.exe"),
        "AMD_GPU0": ("aibenchmark-winml-test", "WinML.exe"),
        "AMD_GPU1": ("aibenchmark-winml-test", "WinML.exe"),
        "Intel_CPU": ("aibenchmark-openvino-test", "OpenVino.exe"),
        "Intel_GPU0": ("aibenchmark-openvino-test", "OpenVino.exe"),
        "Intel_GPU1": ("aibenchmark-openvino-test", "OpenVino.exe"),
        "Intel_NPU": ("aibenchmark-openvino-test", "OpenVino.exe"),
        "NVIDIA_GPU": ("aibenchmark-tensorrt-test", "TensorRT.exe"),
        "Qualcomm_HTP": ("aibenchmark-snpe-test", "SNPE.exe"),
    }
    folder, exe = engine_config[args.engine]

    chops_path = f"C:\\ProgramData\\UL\\Procyon\\chops\\dlc\\{folder}\\x64"

    if not chops_path:
        logger.info("Installation path not found.")
        return None

    exe_path = os.path.join(chops_path, exe)

    if not os.path.exists(exe_path):
        logger.info("Executable %s not found at %s", exe, exe_path)
        return None

    try:
        lang, codepage = win32api.GetFileVersionInfo(
            exe_path, "\\VarFileInfo\\Translation"
        )[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(exe_path, str_info_path)
    except Exception as e:
        logger.info("Error retrieving version info from %s: %s", exe_path, e)
        return None  # Return None if version info retrieval fails
