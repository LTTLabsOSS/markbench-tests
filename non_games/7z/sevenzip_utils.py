"""utility functions for 7-zip harness"""

import os
import shutil


NETWORK_SHARE = r"\\labs.lmg.gg\labs\01_Installers_Utilities\7ZIP"


def copy_from_network_drive(executable_name: str):
    """Download 7zip executable from network drive"""
    source = os.path.join(NETWORK_SHARE, executable_name)
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, executable_name)
    shutil.copyfile(source, destination)
