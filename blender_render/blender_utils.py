
"""Blender render test script"""
from datetime import datetime
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
# pylint: disable=no-name-in-module
from win32api import LOWORD, HIWORD, GetFileVersionInfo

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from harness_utils.misc import download_file, extract_file_from_archive


SCRIPT_DIR = Path(__file__).resolve().parent


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
        download_url="https://svn.blender.org/svnroot/bf-blender/trunk/lib/benchmarks/cycles/barbershop_interior/barbershop_interior.blend"
    ),
    "Monster": BlenderScene(
        name="monster",
        file_name="monster_under_the_bed_sss_demo_by_metin_seven.blend",
        download_url="https://download.blender.org/demo/cycles/monster_under_the_bed_sss_demo_by_metin_seven.blend"
    ),
    "Junkshop": BlenderScene(
        name="junkshop",
        file_name="Junkshop.blend",
        download_url="https://svn.blender.org/svnroot/bf-blender/tags/blender-4.1-release/lib/benchmarks/cycles/junkshop/junkshop.blend"
    ),
    "BMW": BlenderScene(
        name="bmw",
        file_name="bmw27_cpu.blend",
        download_url="https://download.blender.org/demo/test/BMW27_2.blend.zip"
    )
}


def download_scene(scene: BlenderScene) -> None:
    """download blender project to script directory, tries network drive then the internet"""
    destination = SCRIPT_DIR.joinpath(scene.file_name)
    if destination.exists():
        logging.info("%s scene file detected, no downloading required", scene.file_name)
        return

    try:
        logging.info("copying %s from network drive...", scene.file_name)
        copy_scene_from_network_drive(scene.file_name, destination)
        if Path(destination).exists():
            return
    except Exception as ex:
        logging.warning(ex)
        logging.warning("could not download from network drive...")

    try:
        logging.info("downloading %s from internet...", scene.file_name)
        download_file(scene.download_url, destination)
        if scene.name == "bmw":
            extract_file_from_archive(destination, "bmw27/bmw27_cpu.blend", SCRIPT_DIR)
        if destination.exists():
            return
    except Exception as ex:
        logging.error("could not download scene from any source, check connections and try again")
        raise Exception("error downloading scene", cause=ex) from ex


def copy_scene_from_network_drive(file_name, destination):
    """copy blend file from network drive"""
    network_dir = Path("\\\\Labs\\labs\\03_ProcessingFiles\\Blender Render")
    source_path = network_dir.joinpath(file_name)
    logging.info("Copying %s from %s", file_name, source_path)
    shutil.copyfile(source_path, destination)


def time_to_seconds(time_string):
    """convert string to duration in seconds"""
    colon_count = time_string.count(':')
    time_format = "%H:%M:%S.%f"
    if colon_count < 2:
        time_format = "%M:%S.%f"
    time_obj = datetime.strptime(time_string, time_format)
    seconds = (time_obj.hour * 3600) + (time_obj.minute * 60) + time_obj.second + (time_obj.microsecond / 1e6)
    return seconds


def run_blender_render(executable_path: Path, log_directory: Path, device: str, benchmark: BlenderScene) -> str:
    """Execute the blender render of barbershop, returns the duration as string"""
    blend_log = log_directory.joinpath("blender.log")
    blend_path = SCRIPT_DIR.joinpath(benchmark.file_name)
    cmd_line = f"\"{str(executable_path)}\" -b -E CYCLES -y \"{str(blend_path)}\" -f 1 -- --cycles-device {device} --cycles-print-stats"
    with open(blend_log,'w' , encoding="utf-8") as f_obj:
        subprocess.run(cmd_line, stdout=f_obj, text=True, check=True)

    # example: Time: 02:59.57 (Saving: 00:00.16)
    time_regex = r"Time: (.*) \(Saving.*\)"

    time = None
    with open(blend_log, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        lines.reverse()
        count = 0
        for line in lines:
            count += 1
            match = re.match(time_regex, line.strip())
            if match:
                time = match.group(1)
                break
    return time_to_seconds(time)


def find_blender():
    """Find installed blender and return path and version"""
    blender_dir = Path("C:\\Program Files\\Blender Foundation\\")
    versions = []
    if not blender_dir.exists():
        raise Exception("Blender not detected")
    for directory in os.listdir(blender_dir):
        # expecting subdir following pattern of Blender 3.6, Blender 3.5, etc.
        versions.append(directory.replace("Blender", "").strip())
    versions.sort(reverse=True)
    latest_ver = versions[0]
    executable_path = blender_dir.joinpath(f"Blender {latest_ver}", "blender.exe")
    if not executable_path.exists():
        raise Exception("Blender not detected")
    info = GetFileVersionInfo(executable_path, "\\")
    version_ms = info['FileVersionMS']
    version_ls = info['FileVersionLS']
    version = f"{HIWORD (version_ms)}.{LOWORD (version_ms)}.{HIWORD (version_ls)}.{LOWORD (version_ls)}"
    return executable_path, version
