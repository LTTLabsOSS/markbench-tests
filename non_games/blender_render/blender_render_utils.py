# ruff: noqa: DTZ007
"""Blender render test script"""

import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import requests

logger = logging.getLogger(__name__)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

WINDOWS_NETWORK_DIR = Path(
    r"\\labs.lmg.gg\labs\03_ProcessingFiles\Blender Render"
)

LINUX_NETWORK_DIR = Path(
    "/mnt/labs.lmg.gg/labs/03_ProcessingFiles/Blender Render"
)


@dataclass
class BlenderScene:
    """a renderable blender project"""

    name: str
    file_name: str
    download_url: str


BENCHMARK_CONFIG = {
    "Barbershop": BlenderScene(
        name="barbershop",
        file_name="barbershop_interior.blend",
        download_url="https://svn.blender.org/svnroot/bf-blender/trunk/lib/benchmarks/cycles/barbershop_interior/barbershop_interior.blend",
    ),
    "Monster": BlenderScene(
        name="monster",
        file_name="monster_under_the_bed_sss_demo_by_metin_seven.blend",
        download_url="https://download.blender.org/demo/cycles/monster_under_the_bed_sss_demo_by_metin_seven.blend",
    ),
    "Junkshop": BlenderScene(
        name="junkshop",
        file_name="Junkshop.blend",
        download_url="https://svn.blender.org/svnroot/bf-blender/tags/blender-4.1-release/lib/benchmarks/cycles/junkshop/junkshop.blend",
    ),
    "BMW": BlenderScene(
        name="bmw",
        file_name="bmw27_cpu.blend",
        download_url="https://download.blender.org/demo/test/BMW27_2.blend.zip",
    ),
}


def download_scene(scene: BlenderScene) -> None:
    """download blender project to script directory, tries network drive then the internet"""
    destination = SCRIPT_DIRECTORY.joinpath(scene.file_name)
    if destination.exists():
        logger.info("%s scene file detected, no downloading required", scene.file_name)
        return

    try:
        copy_scene_from_network_drive(scene.file_name, destination)
        if destination.exists():
            return
    except Exception as ex:
        logger.warning(ex)
        logger.warning("could not download from network drive...")

    try:
        logger.info("downloading %s from internet...", scene.file_name)
        response = requests.get(scene.download_url, allow_redirects=True, timeout=120)
        with open(destination, "wb") as f:
            f.write(response.content)
        if scene.name == "bmw":
            with ZipFile(destination, "r") as zip_object:
                zip_object.extract("bmw27/bmw27_cpu.blend", path=SCRIPT_DIRECTORY)
        if destination.exists():
            return
    except Exception as ex:
        logger.error(
            "could not download scene from any source, check connections and try again"
        )
        raise RuntimeError("error downloading scene") from ex


def copy_scene_from_network_drive(
    file_name: str,
    destination: Path,
) -> None:
    """Copy Blender scene from network drive."""

    operating_system = platform.system()

    if operating_system == "Windows":
        network_dir = WINDOWS_NETWORK_DIR
    elif operating_system == "Linux":
        network_dir = LINUX_NETWORK_DIR
    else:
        raise RuntimeError(
            f"Unsupported operating system: {operating_system}"
        )

    source_path = network_dir.joinpath(file_name)

    logger.info(
        "Copying %s from %s",
        file_name,
        source_path,
    )

    shutil.copyfile(source_path, destination)


def time_to_seconds(time_string):
    """convert string to duration in seconds"""
    colon_count = time_string.count(":")
    time_format = "%H:%M:%S.%f"
    if colon_count < 2:
        time_format = "%M:%S.%f"
    time_obj = datetime.strptime(time_string, time_format)
    seconds = (
        (time_obj.hour * 3600)
        + (time_obj.minute * 60)
        + time_obj.second
        + (time_obj.microsecond / 1e6)
    )
    return seconds


def run_blender_render(
    executable_path: Path,
    log_directory: Path,
    device: str,
    benchmark: BlenderScene,
) -> float:
    """Execute the Blender render and return the render duration."""
    blend_log = log_directory.joinpath("blender.log")
    blend_path = SCRIPT_DIRECTORY.joinpath(benchmark.file_name)

    command = [
        str(executable_path),
        "-b",
        "-E",
        "CYCLES",
        "-y",
        str(blend_path),
        "-f",
        "1",
        "--",
        "--cycles-device",
        device,
        "--cycles-print-stats",
    ]

    with open(blend_log, "w", encoding="utf-8") as f_obj:
        subprocess.run(
            command,
            stdout=f_obj,
            text=True,
            check=True,
        )

    # Example:
    # Time: 02:59.57 (Saving: 00:00.16)
    time_regex = r"Time:\s+([\d:.]+)\s+\(Saving"

    with open(blend_log, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in reversed(lines):
        match = re.search(time_regex, line)

        if match:
            return time_to_seconds(match.group(1))

    raise RuntimeError(
        f"Could not find render duration in Blender log: {blend_log}"
    )


def get_blender_version(executable_path: Path) -> str:
    """Get the actual Blender version reported by the executable."""
    result = subprocess.run(
        [str(executable_path), "--version"],
        capture_output=True,
        text=True,
        check=True,
    )

    match = re.search(
        r"Blender\s+(\d+(?:\.\d+)+)",
        result.stdout,
    )

    if not match:
        raise RuntimeError(
            f"Could not determine Blender version from {executable_path}"
        )

    return match.group(1)


def find_blender() -> tuple[Path, str]:
    """Find Blender and return its executable path and actual version."""
    if sys.platform == "win32":
        blender_dir = Path(r"C:\Program Files\Blender Foundation")

        if not blender_dir.exists():
            raise RuntimeError("Blender not detected")

        version_pattern = re.compile(
            r"^Blender\s+(\d+(?:\.\d+)*)$"
        )

        versions = []

        for directory in blender_dir.iterdir():
            if not directory.is_dir():
                continue

            match = version_pattern.match(directory.name)

            if match:
                versions.append(match.group(1))

        if not versions:
            raise RuntimeError("Blender not detected")

        latest_version = max(
            versions,
            key=lambda version: tuple(
                int(part) for part in version.split(".")
            ),
        )

        executable_path = (
            blender_dir
            / f"Blender {latest_version}"
            / "blender.exe"
        )

    else:
        blender_executable = shutil.which("blender")

        if blender_executable is None:
            raise RuntimeError("Blender not detected")

        executable_path = Path(blender_executable)

    if not executable_path.exists():
        raise RuntimeError(
            f"Blender executable not detected: {executable_path}"
        )

    version = get_blender_version(executable_path)

    logger.info("Found Blender executable: %s", executable_path)
    logger.info("Blender executable version: %s", version)

    return executable_path, version
