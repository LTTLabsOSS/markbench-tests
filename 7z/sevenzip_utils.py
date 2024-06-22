import os
import shutil


def copy_from_network_drive():
    """Download 7zip from network drive"""
    source = r"\\Labs\labs\01_Installers_Utilities\7ZIP\7zr_24.07.exe"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, "7zr_24.07.exe")
    shutil.copyfile(source, destination)