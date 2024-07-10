"""utility functions for xz test script"""

import os
from pathlib import Path
import time
import shutil

XZ_EXECUTABLE = "xz_5.6.2_x86_64.exe"
SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def xz_executable_exists() -> bool:
    """Check if xz has been downloaded or not"""
    return os.path.isfile(os.path.join(SCRIPT_DIR, XZ_EXECUTABLE))


def copy_from_network_drive():
    """Download xz from network drive"""
    source = r"\\Labs\labs\01_Installers_Utilities\xz\xz_5.6.2_x86_64.exe"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, XZ_EXECUTABLE)
    shutil.copyfile(source, destination)

    source = r"\\Labs\labs\03_ProcessingFiles\Compression\tq_dlss_explained_1080p.mp4"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, "tq_dlss_explained_1080p.mp4")
    shutil.copyfile(source, destination)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
