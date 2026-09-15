"""Collection of functions to assist in running of primesieve test script."""

import ctypes
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


def get_windows_architecture() -> str:
    """Determine the native Windows architecture."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    is_wow64_process2 = kernel32.IsWow64Process2
    is_wow64_process2.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_ushort),
        ctypes.POINTER(ctypes.c_ushort),
    ]
    is_wow64_process2.restype = ctypes.c_bool

    process_machine = ctypes.c_ushort()
    native_machine = ctypes.c_ushort()

    result = is_wow64_process2(
        kernel32.GetCurrentProcess(),
        ctypes.byref(process_machine),
        ctypes.byref(native_machine),
    )

    if not result:
        error_code = ctypes.get_last_error()
        raise RuntimeError(
            f"Unable to determine Windows architecture. "
            f"Windows error: {error_code}"
        )

    # IMAGE_FILE_MACHINE_ARM64
    if native_machine.value == 0xAA64:
        return "ARM64"

    # IMAGE_FILE_MACHINE_AMD64
    if native_machine.value == 0x8664:
        return "AMD64"

    raise RuntimeError(
        f"Unsupported native Windows architecture: "
        f"0x{native_machine.value:04X}"
    )


if platform.system() == "Windows":
    WINDOWS_ARCHITECTURE = get_windows_architecture()

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


def get_primesieve_executable() -> Path:
    """Get the path to the PrimeSieve executable."""
    if platform.system() != "Windows":
        raise RuntimeError(
            "This function is only supported on Windows."
        )

    executable_path = (
        SCRIPT_DIRECTORY
        / "primesieve.exe"
    )

    if not executable_path.is_file():
        raise RuntimeError(
            f"PrimeSieve executable was not found at: "
            f"{executable_path}"
        )

    return executable_path


def primesieve_exe_exists() -> bool:
    """Check if primesieve has been downloaded or not."""
    if platform.system() != "Windows":
        return False

    return (
        SCRIPT_DIRECTORY
        / "primesieve.exe"
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
    """Get the PrimeSieve version from the executable."""
    output = subprocess.check_output(
        [executable_path, "-v"],
        text=True,
        stderr=subprocess.STDOUT,
    )

    version_match = re.search(
        r"primesieve\s+([\d.]+)",
        output,
        re.IGNORECASE,
    )

    if version_match is None:
        raise RuntimeError(
            f"Unable to determine PrimeSieve version from output:\n{output}"
        )

    return version_match.group(1)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch."""
    return int(time.time() * 1000)