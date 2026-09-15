"""Collection of functions to assist in running of primesieve test script."""

import platform
import time
from pathlib import Path
from zipfile import ZipFile

import requests

PRIMESIEVE_VERSION = "12.3"

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

WINDOWS_ARCHIVE_NAMES = {
    "AMD64": "primesieve-12.3-win-x64.zip",
    "ARM64": "primesieve-12.3-win-arm64.zip",
}


if platform.system() == "Windows":
    WINDOWS_ARCHITECTURE = platform.machine().upper()

    if WINDOWS_ARCHITECTURE not in WINDOWS_ARCHIVE_NAMES:
        raise RuntimeError(
            f"Unsupported Windows architecture: {WINDOWS_ARCHITECTURE}"
        )

    PRIMESIEVE_ARCHIVE_NAME = WINDOWS_ARCHIVE_NAMES[WINDOWS_ARCHITECTURE]
    PRIMESIEVE_FOLDER_NAME = PRIMESIEVE_ARCHIVE_NAME.removesuffix(".zip")

    PRIMESIEVE_DOWNLOAD_URL = (
        f"https://github.com/kimwalisch/primesieve/releases/download/"
        f"v{PRIMESIEVE_VERSION}/{PRIMESIEVE_ARCHIVE_NAME}"
    )
else:
    PRIMESIEVE_FOLDER_NAME = ""
    PRIMESIEVE_ARCHIVE_NAME = ""
    PRIMESIEVE_DOWNLOAD_URL = ""


def primesieve_folder_exists() -> bool:
    """Check if primesieve has been downloaded or not."""
    if platform.system() != "Windows":
        return False

    return (SCRIPT_DIRECTORY / PRIMESIEVE_FOLDER_NAME).is_dir()


def download_primesieve():
    """Download and extract primesieve on Windows."""
    if platform.system() != "Windows":
        raise RuntimeError(
            "PrimeSieve downloads are only supported on Windows."
        )

    destination = SCRIPT_DIRECTORY / PRIMESIEVE_ARCHIVE_NAME

    response = requests.get(
        PRIMESIEVE_DOWNLOAD_URL,
        allow_redirects=True,
        timeout=180,
    )
    response.raise_for_status()

    with destination.open("wb") as file:
        file.write(response.content)

    destination_folder = SCRIPT_DIRECTORY / PRIMESIEVE_FOLDER_NAME

    with ZipFile(destination, "r") as zip_object:
        zip_object.extractall(path=SCRIPT_DIRECTORY)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch."""
    return int(time.time() * 1000)