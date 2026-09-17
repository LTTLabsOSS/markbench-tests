"""Utility script for FFmpeg encoding tests."""

import platform
import shutil
import subprocess
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

OPERATING_SYSTEM = platform.system()

if OPERATING_SYSTEM == "Windows":
    NETWORK_FFMPEG_ROOT = Path(
        r"\\labs.lmg.gg\labs\01_Installers_Utilities\ffmpeg"
    )
    NETWORK_SOURCE_ROOT = Path(
        r"\\labs.lmg.gg\labs\03_ProcessingFiles\Handbrake Test"
    )
    FFMPEG_EXECUTABLE = "ffmpeg.exe"

elif OPERATING_SYSTEM == "Linux":
    NETWORK_FFMPEG_ROOT = Path(
        "/mnt/labs.lmg.gg/labs/01_Installers_Utilities/ffmpeg"
    )
    NETWORK_SOURCE_ROOT = Path(
        "/mnt/labs.lmg.gg/labs/03_ProcessingFiles/Handbrake Test"
    )
    FFMPEG_EXECUTABLE = "ffmpeg"

else:
    raise OSError(
        f"Unsupported operating system: {OPERATING_SYSTEM}"
    )


TEST_OPTIONS = {
    "x86_64": {
        "windows": "ffmpeg-n9.0.1-31-g3a7c002718-win64-gpl-9.0.zip",
        "linux": "ffmpeg-n9.0.1-31-g3a7c002718-linux64-gpl-9.0.tar.xz",
    },
    "arm64": {
        "windows": "ffmpeg-n9.0.1-31-g3a7c002718-winarm64-gpl-9.0.zip",
        "linux": "ffmpeg-n9.0.1-31-g3a7c002718-linuxarm64-gpl-9.0.tar.xz",
    },
}

SOURCE_VIDEO_NAME = "big_buck_bunny_1080p24.y4m"
SOURCE_VIDEO = SCRIPT_DIRECTORY / SOURCE_VIDEO_NAME
SOURCE_VIDEO_URL = (
    "https://media.xiph.org/video/derf/y4m/"
    "big_buck_bunny_1080p24.y4m.xz"
)

VMAF_VERSION = "vmaf_v0.6.1neg"

GITHUB_FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/"
    "autobuild-2026-09-16-19-44/"
)


def get_ffmpeg_archive_name(architecture):
    """Return the FFmpeg archive name for the selected architecture."""
    platform_name = "windows" if OPERATING_SYSTEM == "Windows" else "linux"

    try:
        return TEST_OPTIONS[architecture][platform_name]
    except KeyError:
        raise ValueError(
            f"Unsupported architecture: {architecture}"
        )


def get_ffmpeg_root(architecture):
    """Return the expected extracted FFmpeg directory."""
    archive_name = get_ffmpeg_archive_name(architecture)

    if archive_name.endswith(".tar.xz"):
        directory_name = archive_name[:-7]
    elif archive_name.endswith(".zip"):
        directory_name = archive_name[:-4]
    else:
        raise ValueError(
            f"Unsupported FFmpeg archive format: {archive_name}"
        )

    return SCRIPT_DIRECTORY / directory_name


def get_ffmpeg_exe_path(architecture):
    """Return the path to the FFmpeg executable."""
    return get_ffmpeg_root(architecture) / "bin" / FFMPEG_EXECUTABLE


def get_ffmpeg_version(architecture):
    """Return the installed FFmpeg version, or None when FFmpeg is unavailable."""
    ffmpeg_exe = get_ffmpeg_exe_path(architecture)

    if not ffmpeg_exe.is_file():
        return None

    try:
        result = subprocess.run(
            [str(ffmpeg_exe), "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    first_line = result.stdout.splitlines()[0] if result.stdout else ""

    if not first_line.startswith("ffmpeg version "):
        return None

    version = first_line.removeprefix("ffmpeg version ").split()[0]
    parts = version.split("-")

    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"

    return version


def get_ffmpeg(architecture):
    """Return a working FFmpeg executable and its version, acquiring it if needed."""
    ffmpeg_exe = get_ffmpeg_exe_path(architecture)
    ffmpeg_version = get_ffmpeg_version(architecture)

    if ffmpeg_version:
        print(f"FFmpeg already working: {ffmpeg_version}")
        return ffmpeg_exe, ffmpeg_version

    archive_name = get_ffmpeg_archive_name(architecture)
    local_archive = SCRIPT_DIRECTORY / archive_name
    network_archive = NETWORK_FFMPEG_ROOT / archive_name

    try:
        if network_archive.is_file():
            print(f"Copying FFmpeg from network: {archive_name}")
            shutil.copyfile(network_archive, local_archive)

        else:
            raise FileNotFoundError(
                f"FFmpeg archive not found on network: {network_archive}"
            )

    except OSError:
        url = GITHUB_FFMPEG_URL + archive_name

        print(f"FFmpeg not available on network drive.")
        print(f"Downloading FFmpeg from GitHub: {archive_name}")

        urllib.request.urlretrieve(url, local_archive)

    print(f"Extracting FFmpeg: {archive_name}")

    if archive_name.endswith(".zip"):
        with zipfile.ZipFile(local_archive, "r") as archive:
            archive.extractall(SCRIPT_DIRECTORY)

    elif archive_name.endswith(".tar.xz"):
        with tarfile.open(local_archive, "r:xz") as archive:
            archive.extractall(SCRIPT_DIRECTORY)

    else:
        raise ValueError(
            f"Unsupported FFmpeg archive format: {archive_name}"
        )

    ffmpeg_version = get_ffmpeg_version(architecture)

    if not ffmpeg_version:
        raise RuntimeError(
            f"FFmpeg was extracted but is not working: {ffmpeg_exe}"
        )

    print(f"FFmpeg ready: {ffmpeg_version}")

    return ffmpeg_exe, ffmpeg_version


def copy_vmaf(architecture):
    """Copy the VMAF folder from the network when the local VMAF model is missing."""
    ffmpeg_root = get_ffmpeg_root(architecture)

    local_vmaf = ffmpeg_root / "vmaf"
    local_vmaf_model = local_vmaf / f"{VMAF_VERSION}.json"

    if local_vmaf_model.is_file():
        print(f"VMAF already exists: {local_vmaf_model}")
        return

    network_vmaf = NETWORK_FFMPEG_ROOT / "vmaf"

    if not network_vmaf.is_dir():
        raise FileNotFoundError(
            f"VMAF folder not found: {network_vmaf}"
        )

    print(f"Copying VMAF from network: {network_vmaf}")

    shutil.copytree(
        network_vmaf,
        local_vmaf,
        dirs_exist_ok=True,
    )

    if not local_vmaf_model.is_file():
        raise FileNotFoundError(
            f"VMAF model not found after copying: {local_vmaf_model}"
        )


def copy_video_source():
    """Copy the Big Buck Bunny source locally, or provide the manual download URL."""
    if SOURCE_VIDEO.is_file():
        return

    network_source = NETWORK_SOURCE_ROOT / SOURCE_VIDEO_NAME

    try:
        if network_source.is_file():
            print(f"Copying source video from network: {SOURCE_VIDEO_NAME}")
            shutil.copyfile(network_source, SOURCE_VIDEO)
            return
    except OSError:
        pass

    print("Big Buck Bunny source video is not available on the network drive.")
    print("Download it manually from:")
    print(SOURCE_VIDEO_URL)

    raise FileNotFoundError(
        f"Source video not found: {SOURCE_VIDEO}"
    )


def current_time_ms():
    """Return the current Unix timestamp in milliseconds."""
    return int(time.time() * 1000)


def vmaf_supported(architecture):
    """Return True when the selected FFmpeg build reports libvmaf support."""
    try:
        result = subprocess.run(
            [str(get_ffmpeg_exe_path(architecture)), "-filters"],
            capture_output=True,
            text=True,
            check=False,
        )

        output = (result.stdout or "") + (result.stderr or "")

        return "libvmaf" in output.lower()

    except OSError:
        return False