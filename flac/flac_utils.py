"""Collection of functions to assist in running flac test script"""
import os
from zipfile import ZipFile

import requests

FLAC_FOLDER_NAME = "flac-1.4.3-win"
FLAC_ZIP_NAME = "flac-1.4.3-win.zip"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def flac_folder_exists() -> bool:
    """Check if flac has been downloaded or not"""
    return os.path.isdir(os.path.join(SCRIPT_DIR, FLAC_FOLDER_NAME))


def download_flac(url: str) -> str:
    """Download and extract FLAC, return the path to extracted files"""
    destination = os.path.join(SCRIPT_DIR, FLAC_ZIP_NAME)
    response = requests.get(url, allow_redirects=True, timeout=120)
    with open(destination, "wb") as file:
        file.write(response.content)
    with ZipFile(destination, "r") as zip_object:
        zip_object.extractall(path=SCRIPT_DIR)
