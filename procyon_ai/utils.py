"""UL Procyon Computer Vision test utils"""
from pathlib import Path
import psutil
import winreg
import re
import os
import win32api
import sys
from argparse import ArgumentParser
import logging

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"

def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process
    return None

def find_score_in_xml():
    """Reads score from local game log"""
    score_pattern = re.compile(r"<AIOverallScore>(\d+)")
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
    """Gets the path to the Procyon installation directory from the Procyon registry key"""
    reg_path = r"Software\UL\Procyon"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _  = winreg.QueryValueEx(reg_key, "InstallDir")
    return value

def find_procyon_version() -> str:
    """Gets the version of an executable located in the install path."""
    install_path = get_install_path()
    
    if not install_path:
        print("Installation path not found.")
        return None

    exe_path = os.path.join(install_path, "ProcyonCmd.exe")

    if not os.path.exists(exe_path):
        print(f"Executable 'ProcyonCmd.exe' not found at {exe_path}")
        return None

    try:
        lang, codepage = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(exe_path, str_info_path)
    except Exception as e:
        print(f"Error retrieving version info from {exe_path}: {e}")
        return None  # Return None if version info retrieval fails
    
def find_test_version() -> str:
    """Gets the version of an executable located in the chops path."""
    parser = ArgumentParser()
    parser.add_argument(
        "--engine", dest="engine", help="The engine used to run the AI CV", required=True
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
        "Qualcomm_HTP"
    ]

    if args.engine is None or args.engine not in apps:
        logging.info("unrecognized option for program")
        sys.exit(1)

    if args.engine == "AMD_CPU":
        folder = "aibenchmark-winml-test"
        exe = "WinML.exe"
    if args.engine == "AMD_GPU0":
        folder = "aibenchmark-winml-test"
        exe = "WinML.exe"
    if args.engine == "AMD_GPU1":
        folder = "aibenchmark-winml-test"
        exe = "WinML.exe"
    if args.engine == "Intel_CPU":
        folder = "aibenchmark-openvino-test"
        exe = "OpenVino.exe"
    if args.engine == "Intel_GPU0":
        folder = "aibenchmark-openvino-test"
        exe = "OpenVino.exe"
    if args.engine == "Intel_GPU1":
        folder = "aibenchmark-openvino-test"
        exe = "OpenVino.exe"
    if args.engine == "Intel_NPU":
        folder = "aibenchmark-openvino-test"
        exe = "OpenVino.exe"
    if args.engine == "NVIDIA_GPU":
        folder = "aibenchmark-tensorrt-test"
        exe = "TensorRT.exe"
    if args.engine == "Qualcomm_HTP":
        folder = "aibenchmark-snpe-test"
        exe = "SNPE.exe"

    chops_path = f"C:\\ProgramData\\UL\\Procyon\\chops\\dlc\\{folder}\\x64"

    if not chops_path:
        print("Installation path not found.")
        return None

    exe_path = os.path.join(chops_path, exe)

    if not os.path.exists(exe_path):
        print(f"Executable {exe} not found at {exe_path}")
        return None

    try:
        lang, codepage = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(exe_path, str_info_path)
    except Exception as e:
        print(f"Error retrieving version info from {exe_path}: {e}")
        return None  # Return None if version info retrieval fails
    
