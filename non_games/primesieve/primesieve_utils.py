"""Utility functions to assist in running of primesieve test script."""

import ctypes
import logging
import platform
import re
import shutil
import subprocess
import tarfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from zipfile import ZipFile

logger = logging.getLogger(__name__)

PRIMESIEVE_VERSION = "12.15"

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

WINDOWS_NETWORK_SHARE = (
    r"\\labs.lmg.gg\labs\01_Installers_Utilities\primesieve"
)

LINUX_NETWORK_SHARE = (
    "/mnt/labs.lmg.gg/labs/01_Installers_Utilities/primesieve"
)

WINDOWS_ARCHIVE_NAMES = {
    "AMD64": f"primesieve-{PRIMESIEVE_VERSION}-win-x64.zip",
    "ARM64": f"primesieve-{PRIMESIEVE_VERSION}-win-arm64.zip",
}

LINUX_ARCHIVE_NAMES = {
    "x86_64": f"primesieve-{PRIMESIEVE_VERSION}-linux-x64.tar.gz",
    "aarch64": f"primesieve-{PRIMESIEVE_VERSION}-linux-arm64.tar.gz",
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

    if native_machine.value == 0xAA64:
        return "ARM64"

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

    if machine in ("aarch64", "arm64"):
        return "aarch64"

    raise RuntimeError(
        f"Unsupported Linux architecture: {machine}"
    )


if platform.system() == "Windows":
    WINDOWS_ARCHITECTURE = get_windows_architecture()

    if WINDOWS_ARCHITECTURE not in WINDOWS_ARCHIVE_NAMES:
        raise RuntimeError(
            f"Unsupported Windows architecture: "
            f"{WINDOWS_ARCHITECTURE}"
        )

    PRIMESIEVE_ARCHIVE_NAME = (
        WINDOWS_ARCHIVE_NAMES[WINDOWS_ARCHITECTURE]
    )

    PRIMESIEVE_NETWORK_SHARE = WINDOWS_NETWORK_SHARE

    PRIMESIEVE_DOWNLOAD_URL = (
        f"https://github.com/kimwalisch/primesieve/releases/download/"
        f"v{PRIMESIEVE_VERSION}/{PRIMESIEVE_ARCHIVE_NAME}"
    )

elif platform.system() == "Linux":
    LINUX_ARCHITECTURE = get_linux_architecture()

    if LINUX_ARCHITECTURE not in LINUX_ARCHIVE_NAMES:
        raise RuntimeError(
            f"Unsupported Linux architecture: "
            f"{LINUX_ARCHITECTURE}"
        )

    PRIMESIEVE_ARCHIVE_NAME = (
        LINUX_ARCHIVE_NAMES[LINUX_ARCHITECTURE]
    )

    PRIMESIEVE_NETWORK_SHARE = LINUX_NETWORK_SHARE

    # Linux uses the internally built static binaries from the
    # network drive. There is no GitHub download fallback.
    PRIMESIEVE_DOWNLOAD_URL = ""

else:
    PRIMESIEVE_ARCHIVE_NAME = ""
    PRIMESIEVE_NETWORK_SHARE = ""
    PRIMESIEVE_DOWNLOAD_URL = ""


def get_primesieve_executable() -> Path:
    """Get the path to the local PrimeSieve executable."""
    if platform.system() == "Windows":
        executable_path = SCRIPT_DIRECTORY / "primesieve.exe"
    elif platform.system() == "Linux":
        executable_path = SCRIPT_DIRECTORY / "primesieve"
    else:
        raise RuntimeError(
            f"Unsupported operating system: {platform.system()}"
        )

    if not executable_path.is_file():
        raise RuntimeError(
            f"PrimeSieve executable was not found at: "
            f"{executable_path}"
        )

    return executable_path


def primesieve_exe_exists() -> bool:
    """Check if PrimeSieve has already been installed locally."""
    if platform.system() == "Windows":
        executable_path = SCRIPT_DIRECTORY / "primesieve.exe"
    elif platform.system() == "Linux":
        executable_path = SCRIPT_DIRECTORY / "primesieve"
    else:
        return False

    return executable_path.is_file()


def extract_primesieve(archive_path: Path) -> None:
    """Extract the PrimeSieve executable into the script directory."""

    if archive_path.suffix == ".zip":
        with ZipFile(archive_path, "r") as zip_object:
            executable = next(
                (
                    name
                    for name in zip_object.namelist()
                    if Path(name).name == "primesieve.exe"
                ),
                None,
            )

            if executable is None:
                raise RuntimeError(
                    "primesieve.exe was not found in the PrimeSieve archive."
                )

            destination = SCRIPT_DIRECTORY / "primesieve.exe"

            with (
                zip_object.open(executable) as source,
                destination.open("wb") as target,
            ):
                shutil.copyfileobj(source, target)

    elif archive_path.name.endswith(".tar.gz"):
        # First layer: .tar.gz
        with tarfile.open(archive_path, "r:gz") as gz_tar:
            inner_tar_member = next(
                (
                    member
                    for member in gz_tar.getmembers()
                    if member.isfile()
                    and member.name.endswith(".tar")
                ),
                None,
            )

            if inner_tar_member is None:
                raise RuntimeError(
                    "No inner .tar archive was found in "
                    f"{archive_path}"
                )

            inner_tar_file = gz_tar.extractfile(inner_tar_member)

            if inner_tar_file is None:
                raise RuntimeError(
                    f"Unable to extract inner tar from {archive_path}"
                )

            # Second layer: .tar
            with tarfile.open(
                fileobj=inner_tar_file,
                mode="r:",
            ) as inner_tar:
                executable_member = next(
                    (
                        member
                        for member in inner_tar.getmembers()
                        if member.isfile()
                        and Path(member.name).name == "primesieve"
                    ),
                    None,
                )

                if executable_member is None:
                    raise RuntimeError(
                        "primesieve binary was not found in "
                        f"{archive_path}"
                    )

                executable_file = inner_tar.extractfile(
                    executable_member
                )

                if executable_file is None:
                    raise RuntimeError(
                        "Unable to extract primesieve binary from "
                        f"{archive_path}"
                    )

                destination = SCRIPT_DIRECTORY / "primesieve"

                with (
                    executable_file as source,
                    destination.open("wb") as target,
                ):
                    shutil.copyfileobj(source, target)

                destination.chmod(
                    destination.stat().st_mode | 0o111
                )

    else:
        raise RuntimeError(
            f"Unsupported PrimeSieve archive format: {archive_path}"
        )

def copy_from_network_drive() -> bool:
    """
    Copy and extract the appropriate PrimeSieve archive from the
    network drive.

    Returns True if PrimeSieve was installed successfully,
    otherwise False.
    """

    network_share = Path(PRIMESIEVE_NETWORK_SHARE)

    logger.info(
        f"Checking PrimeSieve network share: {network_share}"
    )

    if not network_share.is_dir():
        logger.warning(
            f"PrimeSieve network share is not accessible: "
            f"{network_share}"
        )
        return False

    archive_source = network_share / PRIMESIEVE_ARCHIVE_NAME

    logger.info(
        f"Checking for PrimeSieve archive: {archive_source}"
    )

    if not archive_source.is_file():
        logger.warning(
            f"PrimeSieve archive was not found: "
            f"{archive_source}"
        )
        return False

    archive_destination = (
        SCRIPT_DIRECTORY / PRIMESIEVE_ARCHIVE_NAME
    )

    logger.info(
        f"Copying PrimeSieve archive from network drive: "
        f"{archive_source}"
    )

    try:
        shutil.copyfile(
            archive_source,
            archive_destination,
        )
    except OSError as error:
        logger.warning(
            f"Failed to copy PrimeSieve archive: {error}"
        )
        return False

    logger.info(
        f"Extracting PrimeSieve archive: "
        f"{archive_destination}"
    )

    try:
        extract_primesieve(archive_destination)
    except (OSError, RuntimeError) as error:
        logger.warning(
            f"Failed to extract PrimeSieve archive: {error}"
        )
        return False

    return True


def download_primesieve() -> None:
    """Download PrimeSieve from GitHub."""

    if platform.system() != "Windows":
        raise RuntimeError(
            "GitHub download fallback is only supported on Windows."
        )

    archive_destination = (
        SCRIPT_DIRECTORY / PRIMESIEVE_ARCHIVE_NAME
    )

    logger.info(
        f"Downloading PrimeSieve from {PRIMESIEVE_DOWNLOAD_URL}"
    )

    response = None

    try:
        response = urlopen(
            PRIMESIEVE_DOWNLOAD_URL,
            timeout=180,
        )

        with archive_destination.open("wb") as archive_file:
            shutil.copyfileobj(
                response,
                archive_file,
            )

    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            f"Failed to download PrimeSieve: {error}"
        ) from error

    finally:
        if response is not None:
            response.close()

    extract_primesieve(archive_destination)


def ensure_primesieve() -> Path:
    """Ensure the correct PrimeSieve executable is available."""
    if primesieve_exe_exists():
        logger.info(
            "PrimeSieve binary is already in script directory."
        )
        return get_primesieve_executable()

    if copy_from_network_drive():
        logger.info(
            "PrimeSieve installed from network drive."
        )
        return get_primesieve_executable()

    if platform.system() == "Linux":
        raise RuntimeError(
            "PrimeSieve could not be installed on Linux.\n\n"
            f"Expected network drive: {LINUX_NETWORK_SHARE}\n"
            f"Expected archive: {PRIMESIEVE_ARCHIVE_NAME}\n\n"
            "The PrimeSieve network drive may not be mounted, "
            "or the required PrimeSieve archive may be missing.\n"
            "Mount the L drive and make sure the correct archive "
            "is available, then run the harness again.\n\n"
            f"The benchmark requires PrimeSieve {PRIMESIEVE_VERSION}."
        )

    logger.info(
        "PrimeSieve was not found on the network drive. "
        "Downloading from GitHub."
    )

    download_primesieve()

    return get_primesieve_executable()


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
            f"Unable to determine PrimeSieve version from output:\n"
            f"{output}"
        )

    return version_match.group(1)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch."""
    return int(time.time() * 1000)