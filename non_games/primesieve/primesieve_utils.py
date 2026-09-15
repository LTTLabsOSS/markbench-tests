"""Collection of functions to assist in running of primesieve test script."""

import os
import platform
import re
import subprocess
import time
from pathlib import Path
from zipfile import ZipFile

import requests

PRIMESIEVE_VERSION = "12.15"

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

WINDOWS_ARCHIVE_NAMES = {
    "AMD64": f"primesieve-{PRIMESIEVE_VERSION}-win-x64.zip",
    "ARM64": f"primesieve-{PRIMESIEVE_VERSION}-win-arm64.zip",
}


if platform.system() == "Windows":
    WINDOWS_ARCHITECTURE = (
        os.environ.get("PROCESSOR_ARCHITEW6432")
        or os.environ.get("PROCESSOR_ARCHITECTURE")
    ).upper()

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

    return (
        SCRIPT_DIRECTORY / PRIMESIEVE_FOLDER_NAME / "primesieve.exe"
    ).is_file()


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

    with ZipFile(destination, "r") as zip_object:
        zip_object.extractall(path=SCRIPT_DIRECTORY)


def get_primesieve_version(executable_path: str) -> str:
    """Get the actual PrimeSieve version from the executable."""
    output = subprocess.check_output(
        [executable_path, "--version"],
        text=True,
    )

    version_match = re.search(
        r"primesieve\s+([\d.]+)",
        output,
        re.IGNORECASE,
    )

    if version_match is None:
        raise RuntimeError(
            f"Unable to determine PrimeSieve version from output: {output}"
        )

    return version_match.group(1)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch."""
    return int(time.time() * 1000)