
"""Blender render test script"""
from datetime import datetime
import logging
import os
import re
import shutil
import subprocess
import sys
import requests
# pylint: disable=no-name-in-module
from win32api import LOWORD, HIWORD, GetFileVersionInfo

def copy_from_network_drive():
    """Download barbershop from network drive"""
    source = r"\\Labs\labs\03_ProcessingFiles\Blender Render\barbershop_interior.blend"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, "barbershop_interior.blend")
    shutil.copyfile(source, destination)

def download_barbershop_scene():
    """Downloads blender scene to render"""
    blend_file_name = "barbershop_interior.blend"
    download_url = f"https://svn.blender.org/svnroot/bf-blender/trunk/lib/benchmarks/cycles/barbershop_interior/{blend_file_name}"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, blend_file_name)
    try:
        if os.path.isfile(dest_path) is not True:
            copy_from_network_drive()
    except Exception:
        logging.info("Could not copy barbershop blend file from network share")
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading barbershop scene from internet")
        response = requests.get(
            download_url, allow_redirects=True, timeout=120)
        with open(dest_path, 'wb') as file:
            file.write(response.content)
    logging.info('Barbershop already downloaded')

def time_to_seconds(time_string):
    """convert string to duration in seconds"""
    colon_count = time_string.count(':')
    time_format = "%H:%M:%S.%f"
    if colon_count < 2:
        time_format = "%M:%S.%f"
    time_obj = datetime.strptime(time_string, time_format)
    seconds = (time_obj.hour * 3600) + (time_obj.minute * 60) + time_obj.second + (time_obj.microsecond / 1e6)
    return seconds

def run_blender_render(executable_path: str, log_directory: str, device: str) -> str:
    """Execute the blender render of barbershop, returns the duration as string"""
    blend_log = os.path.join(log_directory, "blender.log")
    root_dir = os.path.dirname(os.path.realpath(__file__))
    blend_path = os.path.join(root_dir, "barbershop_interior.blend")
    cmd_line = f"{executable_path} -b -E CYCLES -y {blend_path} -f 1 -- --cycles-device {device} --cycles-print-stats"
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
    path = "C:\\Program Files\\Blender Foundation\\"
    versions = []
    if os.path.isdir(path) is not True:
        logging.error("Blender not detected")
        sys.exit(1)
    for directory in os.listdir(path):
        # expecting subdir following pattern of Blender 3.6, Blender 3.5, etc.
        versions.append(directory.replace("Blender", "").strip())
    versions.sort(reverse=True)
    latest_ver = versions[0]
    executable_path = os.path.join(path, f"Blender {latest_ver}", "blender.exe")
    if os.path.isfile(executable_path) is not True:
        logging.error("Blender not detected")
        sys.exit(1)
    info = GetFileVersionInfo(executable_path, "\\")
    version_ms = info['FileVersionMS']
    version_ls = info['FileVersionLS']
    version = f"{HIWORD (version_ms)}.{LOWORD (version_ms)}.{HIWORD (version_ls)}.{LOWORD (version_ls)}"
    return executable_path, version


copy_from_network_drive()
