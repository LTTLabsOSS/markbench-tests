"""utility functions for 7-zip harness"""

import os
import platform
import shutil

WINDOWS_NETWORK_SHARE = r"\\labs.lmg.gg\labs\01_Installers_Utilities\7ZIP"
LINUX_NETWORK_SHARE = "/mnt/labs.lmg.gg/labs/01_Installers_Utilities/7ZIP"


def copy_from_network_drive(executable_name: str):
    """Download 7zip executable from network drive."""

    if platform.system() == "Windows":
        network_share = WINDOWS_NETWORK_SHARE
    elif platform.system() == "Linux":
        network_share = LINUX_NETWORK_SHARE
    else:
        raise RuntimeError(
            f"Unsupported operating system: {platform.system()}"
        )

    source = os.path.join(network_share, executable_name)

    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, executable_name)

    shutil.copyfile(source, destination)

    if platform.system() == "Linux":
        os.chmod(destination, os.stat(destination).st_mode | 0o111)