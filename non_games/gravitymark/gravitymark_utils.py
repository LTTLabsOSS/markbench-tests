"""Utility functions for GravityMark test script"""

import ctypes
import getpass
import logging
import platform
import re
import shutil
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

logger = logging.getLogger(__name__)
#================================================
# GLOBALS
#================================================

GRAVITYMARK_VERSION = "1.89"

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

WINDOWS_NETWORK_SHARE = (
    r"\\labs.lmg.gg\labs\01_Installers_Utilities\GravityMark\Windows"
)
LINUX_NETWORK_SHARE = (
    "/mnt/labs.lmg.gg/labs/01_Installers_Utilities/GravityMark/Linux"
)

WINDOWS_INSTALLER_NAMES = {
    "AMD64": f"GravityMark_{GRAVITYMARK_VERSION}.msi",
    "ARM64": f"GravityMark_{GRAVITYMARK_VERSION}_arm64.msi",
}

LINUX_INSTALLER_NAMES = {
    "x86_64": f"GravityMark_{GRAVITYMARK_VERSION}.run",
    "aarch64": f"GravityMark_{GRAVITYMARK_VERSION}_arm64.run",
}

LINUX_GRAVITYMARK_EXTRACT = Path(SCRIPT_DIRECTORY, "GravityMark")

GRAVITYMARK_PATH = Path(SCRIPT_DIRECTORY, "GravityMark", "bin")

#check this if we are going to have it flag if we don't have these set as our option)
SUPPORTED_APIS = {
    ("linux", "x86_64"): {
        "vulkan",
        "opengl",
    },
    ("linux", "aarch64"): {
        "vulkan",
        "opengl",
    },
    ("windows", "x86_64"): {
        "vulkan",
        "opengl",
        "direct3d11",
        "direct3d12",
    },
    ("windows", "arm64"): {
        "direct3d11",
        "direct3d12",
    },
}


#these are the options available in markbench
API_OPTIONS = [
    "vulkan",
    "opengl",
    # "opengles",
    "direct3d12",
    "direct3d11",
    # "metal"
]

ASTEROID_COUNT = {
    "4mil": "4m",
    "2mil": "2m",
    "1mil": "1m",
    "200k": "200k",
    "100k": "100k",
    "50k": "50k",
}

RESOLUTION_OPTION = {
    "2160": "4k",
    "1440": "2k",
    "1080": "fhd",
    "900": "hd+",
    "720": "hd",
}

#required flags for our testing, may need to set more for asteroids, resolution etc (may need configurable options for those)
CLI_OPTIONS = {
    # "-image": str(IMAGE_PATH),
    "-fullscreen": "1",
    "-fps": "1",
    "-info": "1",
    "-sensors": "1",
    "-benchmark": "1",
    "-close": "1",
    "-status": "1",
}

#================================================
# Functions
#================================================
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

    if WINDOWS_ARCHITECTURE not in WINDOWS_INSTALLER_NAMES:
        raise RuntimeError(
            f"Unsupported Windows architecture: "
            f"{WINDOWS_ARCHITECTURE}"
        )

    GRAVITYMARK_INSTALLER_NAME = (
        WINDOWS_INSTALLER_NAMES[WINDOWS_ARCHITECTURE]
    )

    GRAVITYMARK_NETWORK_SHARE = WINDOWS_NETWORK_SHARE

    DOWNLOAD_URL = (
        f"https://tellusim.com/download/"
        f"{GRAVITYMARK_INSTALLER_NAME}"
    )

elif platform.system() == "Linux":
    LINUX_ARCHITECTURE = get_linux_architecture()

    if LINUX_ARCHITECTURE not in LINUX_INSTALLER_NAMES:
        raise RuntimeError(
            f"Unsupported Linux architecture: "
            f"{LINUX_ARCHITECTURE}"
        )

    GRAVITYMARK_INSTALLER_NAME = (
        LINUX_INSTALLER_NAMES[LINUX_ARCHITECTURE]
    )

    GRAVITYMARK_NETWORK_SHARE = LINUX_NETWORK_SHARE

    DOWNLOAD_URL = (
            f"https://tellusim.com/download/"
            f"{GRAVITYMARK_INSTALLER_NAME}"
        )

else:
    GRAVITYMARK_INSTALLER_NAME = ""
    GRAVITYMARK_NETWORK_SHARE = ""
    DOWNLOAD_URL = ""

def verify_gravitymark_version(executable_path: Path) -> str | None:
    """Get the installed GravityMark version."""
    system = platform.system()

    if system == "Windows":
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-Item '{executable_path}').VersionInfo.ProductVersion",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (OSError, subprocess.CalledProcessError) as error:
            logger.warning(
                f"Unable to determine GravityMark version: {error}"
            )
            return None

    if system == "Linux":
        try:
            result = subprocess.run(
                ["strings", str(executable_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            version_pattern = re.compile(r"GravityMark\s+(\d+\.\d+)")

            for line in result.stdout.splitlines():
                match = version_pattern.search(line)
                if match:
                    return match.group(1)

            logger.warning(
                f"Unable to determine GravityMark version from: "
                f"{executable_path}"
            )
            return None

        except OSError as error:
            logger.warning(
                f"Unable to determine GravityMark version: {error}"
            )
            return None

    raise RuntimeError(
        f"Unsupported operating system: {system}"
    )

def get_windows_executable_architecture(executable_path: Path) -> str:
    """Get the architecture of a Windows executable."""
    with executable_path.open("rb") as executable:
        executable.seek(0x3C)
        pe_offset = int.from_bytes(executable.read(4), "little")

        executable.seek(pe_offset + 4)
        machine = int.from_bytes(executable.read(2), "little")

    if machine == 0x8664:
        return "AMD64"

    if machine == 0xAA64:
        return "ARM64"

    raise RuntimeError(
        f"Unsupported Windows executable architecture: "
        f"0x{machine:04X}"
    )

def get_gravitymark_executable() -> tuple[Path, str]:
    """Get the path and version of the local GravityMark executable."""
    system = platform.system()

    if system == "Windows":
        executable_path = GRAVITYMARK_PATH / "GravityMark.exe"
    elif system == "Linux":
        if LINUX_ARCHITECTURE == "x86_64":
            executable_path = GRAVITYMARK_PATH / "GravityMark.x64"
        elif LINUX_ARCHITECTURE == "aarch64":
            executable_path = GRAVITYMARK_PATH / "GravityMark.arm64"
        else:
            raise RuntimeError(
                f"Unsupported Linux architecture: {LINUX_ARCHITECTURE}"
            )
    else:
        raise RuntimeError(
            f"Unsupported operating system: {system}"
        )

    if not executable_path.is_file():
        raise RuntimeError(
            f"GravityMark executable was not found at: {executable_path}"
        )

    if system == "Windows":
        executable_architecture = get_windows_executable_architecture(
            executable_path
        )

        if executable_architecture != WINDOWS_ARCHITECTURE:
            logger.warning(
                f"Incorrect GravityMark architecture detected. "
                f"Found {executable_architecture}, "
                f"but {WINDOWS_ARCHITECTURE} is required."
            )
            raise RuntimeError(
                f"GravityMark {WINDOWS_ARCHITECTURE} is required."
            )

    installed_version = verify_gravitymark_version(executable_path)

    if installed_version is None:
        raise RuntimeError("Unable to determine GravityMark version.")

    if installed_version != GRAVITYMARK_VERSION:
        logger.warning(
            f"Incorrect GravityMark version detected. "
            f"Found {installed_version}, but {GRAVITYMARK_VERSION} is required."
        )
        raise RuntimeError(
            f"GravityMark {GRAVITYMARK_VERSION} is required."
        )

    return executable_path, installed_version

def get_args() -> Namespace:
    """Get command line arguments for test script"""
    parser = ArgumentParser()
    parser.add_argument(
        "-a",
        "--api",
        dest="api",
        required=True,
        choices=API_OPTIONS,
        help="GravityMark graphics API",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        dest="resolution",
        required=True,
        choices=RESOLUTION_OPTION,
        help="GravityMark resolution",
    )
    parser.add_argument(
        "-as",
        "--asteroids",
        dest="asteroids",
        default="200k",
        choices=ASTEROID_COUNT,
        help="GravityMark asteroid count",
    )
    return parser.parse_args()

def install_gravitymark() -> None:
    """Install GravityMark based on OS."""
    gravitymark_installer = (
        SCRIPT_DIRECTORY / GRAVITYMARK_INSTALLER_NAME
    )
    gravitymark_installpath = Path(
        SCRIPT_DIRECTORY,
        "GravityMark",
    )

    if platform.system() == "Windows":
        # Extract GravityMark
        if gravitymark_installpath.exists():
            shutil.rmtree(gravitymark_installpath)

        extract_path = Path(
            SCRIPT_DIRECTORY,
            "GravityMark_extract",
        )

        if extract_path.exists():
            shutil.rmtree(extract_path)

        extract_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            "msiexec",
            "/a",
            str(gravitymark_installer),
            "/qn",
            f"TARGETDIR={extract_path}",
        ]

        logger.info("Extracting GravityMark MSI")
        subprocess.run(command, check=True)

        shutil.move(
            str(extract_path / "GravityMark"),
            str(gravitymark_installpath),
        )

        shutil.rmtree(extract_path)

        if WINDOWS_ARCHITECTURE == "AMD64":
            vc_redist = (
                gravitymark_installpath
                / "bin"
                / "vc_redist.x64.exe"
            )

            if not vc_redist.is_file():
                raise RuntimeError(
                    f"Required VC++ redistributable was not found: {vc_redist}"
                )

            logger.info("Ensuring VC++ x64 Redistributable is installed")

            result = subprocess.run(
                [
                    str(vc_redist),
                    "/install",
                    "/quiet",
                    "/norestart",
                ],
            )

            if result.returncode == 1638:
                logger.info(
                    "VC++ x64 Redistributable is already installed."
                )
            elif result.returncode != 0:
                raise RuntimeError(
                    "VC++ x64 Redistributable installation failed "
                    f"with exit code {result.returncode}"
                )

        get_gravitymark_executable()

    elif platform.system() == "Linux":
        gravitymark_installpath.mkdir(
            parents=True,
            exist_ok=True,
        )

        gravitymark_installer.chmod(
            gravitymark_installer.stat().st_mode | 0o111
        )

        command = [
            str(gravitymark_installer),
            "--tar",
            "xf",
            "-C",
            str(gravitymark_installpath),
        ]

        logger.info("Installing GravityMark")
        subprocess.run(command, check=True)

        get_gravitymark_executable()

def copy_from_network_drive() -> bool:
    """
    Copy the appropriate GravityMark installer from the network drive.

    Returns True if the installer was copied successfully,
    otherwise False.
    """
    network_share = Path(GRAVITYMARK_NETWORK_SHARE)

    try:
        if not network_share.is_dir():
            logger.warning(
                "GravityMark network drive is unavailable: "
                f"{network_share}"
            )
            return False
    except OSError as error:
        logger.warning(
            "GravityMark network drive is unavailable: "
            f"{network_share} ({error})"
        )
        return False

    installer_source = network_share / GRAVITYMARK_INSTALLER_NAME

    try:
        if not installer_source.is_file():
            logger.warning(
                "GravityMark was not found on network drive: "
                f"{installer_source}"
            )
            return False
    except OSError as error:
        logger.warning(
            "Unable to access GravityMark on network drive: "
            f"{installer_source} ({error})"
        )
        return False

    installer_destination = (
        SCRIPT_DIRECTORY / GRAVITYMARK_INSTALLER_NAME
    )

    try:
        shutil.copyfile(
            installer_source,
            installer_destination,
        )
    except OSError as error:
        logger.warning(
            f"Failed to copy GravityMark from network drive: "
            f"{error}"
        )
        return False

    return True


def download_gravitymark() -> None:
    """Download GravityMark from it's website."""
    archive_destination = (
        SCRIPT_DIRECTORY / GRAVITYMARK_INSTALLER_NAME
    )

    logger.info(
        f"Downloading GravityMark from {DOWNLOAD_URL}"
    )

    response = None

    try:
        response = urlopen(
            DOWNLOAD_URL,
            timeout=180,
        )

        with archive_destination.open("wb") as archive_file:
            shutil.copyfileobj(
                response,
                archive_file,
            )

    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            f"Failed to download GravityMark: {error}"
        ) from error

    finally:
        if response is not None:
            response.close()

def ensure_gravitymark() -> tuple[Path, str]:
    """Ensure the required GravityMark version is installed."""
    try:
        executable, version = get_gravitymark_executable()
        logger.info(f"GravityMark {version} is installed.")
        return executable, version
    except RuntimeError:
        logger.info(
            "GravityMark is missing or the incorrect version is installed. "
            "Installing the required version."
        )

    if copy_from_network_drive():
        logger.info("GravityMark installer copied from network share.")
        install_gravitymark()
        return get_gravitymark_executable()

    logger.info(
            "GravityMark could not be installed from the network drive or the version was incorrect. "
            "Downloading from GravityMark's website."
        )
    download_gravitymark()
    install_gravitymark()

    return get_gravitymark_executable()

def get_supported_apis() -> set[str]:
    """Get the graphics APIs supported by the current platform."""

    system = platform.system().lower()

    if system == "windows":
        architecture = (
            "x86_64"
            if WINDOWS_ARCHITECTURE == "AMD64"
            else "arm64"
        )
    elif system == "linux":
        architecture = LINUX_ARCHITECTURE
    else:
        raise RuntimeError(
            f"Unsupported operating system: {platform.system()}"
        )

    return SUPPORTED_APIS[(system, architecture)]


def validate_api(api: str) -> None:
    """Validate that the selected API is supported on this platform."""

    supported_apis = get_supported_apis()

    if api not in supported_apis:
        supported = ", ".join(sorted(supported_apis))
        raise ValueError(
            f"API '{api}' is not supported on "
            f"{platform.system()} {platform.machine()}. "
            f"Supported APIs: {supported}"
        )

def get_gravitymark_log_path() -> Path:
    """Get the path to the GravityMark log file."""

    if platform.system() == "Windows":
        return Path(
            "C:/Users",
            getpass.getuser(),
            ".GravityMark",
            "GravityMark.log",
        )

    if platform.system() == "Linux":
        return Path.home() / ".GravityMark" / "GravityMark.log"

    raise RuntimeError(
        f"Unsupported operating system: {platform.system()}"
    )

def friendly_test_param(api: str) -> str:
    """return a friendlier string given the API harness argument"""
    if api == "vulkan":
        return "Vulkan"
    if api == "opengl":
        return "OpenGL"
    if api == "direct3d12":
        return "DX12"
    if api == "direct3d11":
        return "DX11"
    return api


def get_score(log_path: Path) -> str | None:
    """Parses score value from GravityMark log file"""
    score_pattern = re.compile(r"Score: (\d+)")
    try:
        with log_path.open("r", encoding="utf-8") as file:
            for line in file.readlines():
                match = score_pattern.search(line)
                if match:
                    return match.group(1)
    except OSError:
        return None

    return None

def create_gravitymark_command(
    gravitymark_path: Path,
    api: str,
    ast: str,
    res: str,
    image_path: Path,
):
    """Create the command array for subprocess to run GravityMark."""

    options = [gravitymark_path, api]

    ast_option, ast_value = ast.split()
    options.append(ast_option)
    options.append(ast_value)

    res_option, res_value = res.split()
    options.append(res_option)
    options.append(res_value)

    for arg, value in CLI_OPTIONS.items():
        options.append(arg)
        options.append(value)

    options.append("-image")
    options.append(str(image_path))

    return options
