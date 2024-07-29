"""Collection of functions to assist in running of ycruncher test script"""
import time
from zipfile import ZipFile
from pathlib import Path
import requests

YCRUNCHER_FOLDER_NAME = "y-cruncher.v0.8.5.9543"
YCRUNCHER_ZIP_NAME = "y-cruncher.v0.8.5.9543.zip"

SCRIPT_DIR = Path(__file__).resolve().parent

def ycruncher_folder_exists() -> bool:
    """Check if ycruncher has been downloaded or not"""
    return SCRIPT_DIR.joinpath(YCRUNCHER_FOLDER_NAME).is_dir()


def download_ycruncher():
    """Download and extract Y-Cruncher"""
    download_url = "https://github.com/Mysticial/y-cruncher/releases/download/v0.8.5.9543/y-cruncher.v0.8.5.9543.zip"
    destination = SCRIPT_DIR / YCRUNCHER_ZIP_NAME
    response = requests.get(download_url, allow_redirects=True, timeout=180)
    with open(destination, 'wb') as file:
        file.write(response.content)
    with ZipFile(destination, 'r') as zip_object:
        zip_object.extractall(path=SCRIPT_DIR)

def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
        