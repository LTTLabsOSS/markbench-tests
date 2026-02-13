"""collection of functions to assist in running of primesieve test script"""
import os
from pathlib import Path
import time
from zipfile import ZipFile

import requests

PRIMESIEVE_FOLDER_NAME = "primesieve-12.3-win-x64"
PRIMESIEVE_ZIP_NAME = "primesieve-12.3-win-x64.zip"

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def primesieve_folder_exists() -> bool:
    """Check if primesieve has been downloaded or not"""
    return os.path.isdir(os.path.join(SCRIPT_DIR, PRIMESIEVE_FOLDER_NAME))


def download_primesieve():
    """Download and extract primesieve"""
    download_url = "https://github.com/kimwalisch/primesieve/releases/download/v12.3/primesieve-12.3-win-x64.zip"
    destination = os.path.join(SCRIPT_DIR, PRIMESIEVE_ZIP_NAME)
    response = requests.get(download_url, allow_redirects=True, timeout=180)
    with open(destination, 'wb') as file:
        file.write(response.content)
    with ZipFile(destination, 'r') as zip_object:
        destination_folder = SCRIPT_DIR / PRIMESIEVE_FOLDER_NAME
        zip_object.extractall(path=destination_folder)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
