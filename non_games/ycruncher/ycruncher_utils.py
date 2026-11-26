"""Collection of functions to assist in running of ycruncher test script"""

import ctypes
import platform
import tarfile
import time
import zipfile
from pathlib import Path

import requests

YCRUNCHER_VERSION = "v0.8.7.9547"
SCRIPT_DIRECTORY = Path(__file__).resolve().parent

WINDOWS_ARCHIVE_NAME = {
    "AMD64": f"y-cruncher.{YCRUNCHER_VERSION}.zip"
}

LINUX_ARCHIVE_NAME = {
    "x86_64": f"y-cruncher.{YCRUNCHER_VERSION}-static.tar.xz"
}

# Linux tarball extracts to a different folder name than the zip.
PLATFORM_FOLDER_NAME = {
    "Windows": f"y-cruncher {YCRUNCHER_VERSION}",
    "Linux": f"y-cruncher {YCRUNCHER_VERSION}-static",
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

    if not is_wow64_process2(
        kernel32.GetCurrentProcess(),
        ctypes.byref(process_machine),
        ctypes.byref(native_machine),
    ):
        raise RuntimeError(
            f"Unable to determine Windows architecture. "
            f"Windows error: {ctypes.get_last_error()}"
        )

    if native_machine.value == 0x8664:
        return "AMD64"

    raise RuntimeError(
        f"Unsupported native Windows architecture: "
        f"0x{native_machine.value:04X}"
    )


def get_linux_architecture() -> str:
    """Determine the native Linux architecture."""
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        return "x86_64"

    raise RuntimeError(
        f"Unsupported Linux architecture: {machine}"
    )

def _resolve_platform():
    """Return (system, architecture, archive_name, folder_name)."""
    system = platform.system()

    if system == "Windows":
        arch = get_windows_architecture()
        table = WINDOWS_ARCHIVE_NAME
    elif system == "Linux":
        arch = get_linux_architecture()
        table = LINUX_ARCHIVE_NAME
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    if arch not in table:
        raise RuntimeError(f"Unsupported {system} architecture: {arch}")

    archive_name = table[arch]
    folder_name = PLATFORM_FOLDER_NAME[system]
    return system, arch, archive_name, folder_name


SYSTEM, ARCHITECTURE, YCRUNCHER_ARCHIVE_NAME, YCRUNCHER_FOLDER_NAME = _resolve_platform()

YCRUNCHER_DOWNLOAD_URL = (
    f"https://github.com/Mysticial/y-cruncher/releases/download/"
    f"{YCRUNCHER_VERSION}/{YCRUNCHER_ARCHIVE_NAME}"
)

def ycruncher_folder_exists() -> bool:
    """Check if ycruncher has been downloaded or not"""
    return SCRIPT_DIRECTORY.joinpath(YCRUNCHER_FOLDER_NAME).is_dir()

def get_ycruncher_executable() -> Path:
    """Get the path to the local Y-Cruncher executable."""
    exe_name = "y-cruncher.exe" if SYSTEM == "Windows" else "y-cruncher"
    executable_path = SCRIPT_DIRECTORY / YCRUNCHER_FOLDER_NAME / exe_name

    if not executable_path.is_file():
        raise RuntimeError(
            f"y-cruncher executable was not found at: {executable_path}"
        )
    return executable_path

def download_ycruncher():
    """Download and extract Y-Cruncher"""
    destination = SCRIPT_DIRECTORY / YCRUNCHER_ARCHIVE_NAME
    response = requests.get(YCRUNCHER_DOWNLOAD_URL, allow_redirects=True, timeout=180)
    response.raise_for_status()
    with open(destination, "wb") as file:
        file.write(response.content)
    if YCRUNCHER_ARCHIVE_NAME.endswith(".zip"):
        with zipfile.ZipFile(destination, "r") as archive:
            archive.extractall(SCRIPT_DIRECTORY)

    elif YCRUNCHER_ARCHIVE_NAME.endswith(".tar.xz"):
        with tarfile.open(destination, "r:xz") as archive:
            archive.extractall(SCRIPT_DIRECTORY)

    else:
        raise ValueError(
            f"Unsupported Y-Cruncher archive format: {YCRUNCHER_ARCHIVE_NAME}"
        )


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
