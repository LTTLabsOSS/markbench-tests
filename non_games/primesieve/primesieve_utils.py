"""Collection of functions to assist in running of primesieve test script."""

import os
import platform
import re
import subprocess
import time
from pathlib import Path
from zipfile import ZipFile

import requests

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

GITHUB_RELEASES_URL = (
    "https://api.github.com/repos/kimwalisch/primesieve/releases/latest"
)


def get_latest_windows_release():
    """Get the latest PrimeSieve Windows release information."""
    architecture = os.environ.get("PROCESSOR_ARCHITEW6432")

    if architecture is None:
        architecture = os.environ.get("PROCESSOR_ARCHITECTURE")

    architecture = architecture.upper()

    if architecture == "AMD64":
        architecture_name = "x64"
    elif architecture == "ARM64":
        architecture_name = "arm64"
    else:
        raise RuntimeError(
            f"Unsupported Windows architecture: {architecture}"
        )

    response = requests.get(
        GITHUB_RELEASES_URL,
        timeout=30,
        headers={"Accept": "application/vnd.github+json"},
    )
    response.raise_for_status()

    release = response.json()

    version = release["tag_name"].lstrip("v")

    expected_archive_name = (
        f"primesieve-{version}-win-{architecture_name}.zip"
    )

    for asset in release["assets"]:
        if asset["name"] == expected_archive_name:
            return version, expected_archive_name

    raise RuntimeError(
        f"PrimeSieve Windows {architecture_name} archive was not found "
        f"in the latest release ({version})."
    )


def get_primesieve_executable() -> Path:
    """Get the path to the latest PrimeSieve Windows executable."""
    if platform.system() != "Windows":
        raise RuntimeError(
            "This function is only supported on Windows."
        )

    _, archive_name = get_latest_windows_release()

    folder_name = archive_name.removesuffix(".zip")

    executable_path = (
        SCRIPT_DIRECTORY / folder_name / "primesieve.exe"
    )

    return executable_path


def primesieve_folder_exists() -> bool:
    """Check if the latest PrimeSieve Windows version is downloaded."""
    if platform.system() != "Windows":
        return False

    executable_path = get_primesieve_executable()

    return executable_path.is_file()


def download_primesieve():
    """Download and extract the latest PrimeSieve Windows release."""
    if platform.system() != "Windows":
        raise RuntimeError(
            "PrimeSieve downloads are only supported on Windows."
        )

    version, archive_name = get_latest_windows_release()

    download_url = (
        f"https://github.com/kimwalisch/primesieve/releases/download/"
        f"v{version}/{archive_name}"
    )

    destination = SCRIPT_DIRECTORY / archive_name

    response = requests.get(
        download_url,
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