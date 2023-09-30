"""Collection of functions to assist in running of ycruncher test script"""
import os
from zipfile import ZipFile

import requests

YCRUNCHER_FOLDER_NAME = "y-cruncher v0.8.2.9522"
YCRUNCHER_ZIP_NAME = "y-cruncher v0.8.2.9522.zip"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def ycruncher_folder_exists() -> bool:
    """Check if ycruncher has been downloaded or not"""
    return os.path.isdir(os.path.join(SCRIPT_DIR, YCRUNCHER_FOLDER_NAME))


def download_ycruncher():
    """Download and extract Y-Cruncher"""
    download_url = "http://www.numberworld.org/y-cruncher/old_versions/y-cruncher%20v0.8.2.9522.zip"
    destination = os.path.join(SCRIPT_DIR, YCRUNCHER_ZIP_NAME)
    response = requests.get(download_url, allow_redirects=True, timeout=180)
    with open(destination, "wb") as file:
        file.write(response.content)
    with ZipFile(destination, "r") as zip_object:
        zip_object.extractall(path=SCRIPT_DIR)
