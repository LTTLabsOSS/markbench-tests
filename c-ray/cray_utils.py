"""collection of functions to assist in running of primesieve test script"""
import os
from pathlib import Path
import time
import shutil

CRAY_EXECUTABLE = "c-ray-fast_x86_64.exe"
SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def cray_executable_exists() -> bool:
    """Check if cray has been downloaded or not"""
    return os.path.isfile(os.path.join(SCRIPT_DIR, CRAY_EXECUTABLE))


def copy_from_network_drive():
    """Download cray from network drive"""
    source = r"\\Labs\labs\01_Installers_Utilities\C-Ray\c-ray-fast_x86_64.exe"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, CRAY_EXECUTABLE)
    shutil.copyfile(source, destination)

    source = r"\\Labs\labs\01_Installers_Utilities\C-Ray\sphfract.scn"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, "sphfract.scn")
    shutil.copyfile(source, destination)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
