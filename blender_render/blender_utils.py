
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
from argparse import ArgumentParser
from zipfile import ZipFile

BENCHMARK_CONFIG = {
    "Barbershop": "barbershop_interior.blend",
    "Monster": "monster_under_the_bed_sss_demo_by_metin_seven.blend",
    "Junkshop": "Junkshop.blend",
    "BMW": "bmw27_cpu.blend",
    
}

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

parser = ArgumentParser()
parser.add_argument("-d", "--device", dest="device",
                    help="device", metavar="device", required=True)
parser.add_argument(
        "--benchmark", dest="benchmark", help="Benchmark test type", metavar="benchmark", required=True)
args = parser.parse_args()

benchmark = args.benchmark

def download_scene(benchmark):
    if benchmark == "Barbershop":
        download_barbershop_scene()
    if benchmark == "Monster":
        download_monster_scene()
    if benchmark == "Junkshop":
        download_junkshop_scene()
    if benchmark == "BMW":
        download_bmw_scene()

def copy_from_network_drive():
    """Download barbershop from network drive"""
    sourcepath = r'\\Labs\labs\03_ProcessingFiles\Blender Render'
    sourcefile = BENCHMARK_CONFIG[args.benchmark]
    source = os.path.join(sourcepath, sourcefile)
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, sourcefile)
    shutil.copyfile(source, destination)
    logging.info(f"Copying file from {source}")



def download_barbershop_scene():
    """Downloads blender scene to render"""
    blend_file_name = "barbershop_interior.blend"
    download_url = f"https://svn.blender.org/svnroot/bf-blender/trunk/lib/benchmarks/cycles/barbershop_interior/{blend_file_name}"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, blend_file_name)
    try:
        if os.path.isfile(dest_path) is not True:
            copy_from_network_drive()
        else:
            logging.info('Barbershop already downloaded')
    except Exception:
        logging.info("Could not copy barbershop blend file from network share")
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading barbershop scene from internet")
        response = requests.get(
            download_url, allow_redirects=True, timeout=120)
        with open(dest_path, 'wb') as file:
            file.write(response.content)
 

def download_bmw_scene():
    """Downloads blender scene to render"""
    blend_file_name = BENCHMARK_CONFIG[args.benchmark]
    download_url = f"https://download.blender.org/demo/test/BMW27_2.blend.zip"
    zip_file = "BMW27_2.blend.zip"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, blend_file_name)
    zip_extract = os.path.join(root_dir, zip_file)
    try:
        if os.path.isfile(dest_path) is not True:
            copy_from_network_drive()
        else:
            logging.info('BMW already downloaded')
    except Exception:
        logging.info("Could not copy BMW blend file from network share")
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading BMW scene from internet")
        response = requests.get(download_url, allow_redirects=True, timeout=120)
        with open(zip_extract, 'wb') as file:
            file.write(response.content)
        with ZipFile(zip_extract, 'r') as zip_object:
            zip_object.extract("bmw27/bmw27_cpu.blend", path=root_dir)


def download_monster_scene():
    """Downloads blender scene to render"""
    blend_file_name = BENCHMARK_CONFIG[args.benchmark]
    download_url = f"https://download.blender.org/demo/cycles/{blend_file_name}"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, blend_file_name)
    try:
        if os.path.isfile(dest_path) is not True:
            copy_from_network_drive()
        else:
            logging.info('Monster already downloaded')
    except Exception:
        logging.info("Could not copy monster blend file from network share")
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading monster scene from internet")
        response = requests.get(
            download_url, allow_redirects=True, timeout=120)
        with open(dest_path, 'wb') as file:
            file.write(response.content)


def download_junkshop_scene():
    """Downloads blender scene to render"""
    blend_file_name = "Blender 2.blend"
    download_url = f"https://storage.googleapis.com/5649de716dcaf85da2faee95/_%2F35a35553b3dd4f8c8fb5a6ccc5065ff1.blend?GoogleAccessId=956532172770-27ie9eb8e4u326l89p7b113gcb04cdgd%40developer.gserviceaccount.com&Expires=1722324107&Signature=M0Im7Y61zF81JvFobeb1ZzOY%2FQP23Pbu%2B%2BjRjSPpyzfxDWaEgAKsceevZ5XV0OjJ2LDli2C6Bp%2BXhNvO8XfNLrTtCiPeFLHc02Bhm7T0%2B3FzpMmfauuCBvP0MKqMZGeMHD1z4ci7OFfsfsXYXBCuFx1FxaMNgZpkrv16gK13Hu%2BkhnIQUuR8q1iHHecXTUodRTfo2r6fQf8Y%2B9g4ysGuMMMY3o4SYZVE%2Flw0VdDMtjCIvc00uOwWM%2Fdyvt%2BDEbM9aEvD4yK2Iep0eMDRaPSE3xFAXcXgYHIZhB9zznVxHBeO6NKati%2F%2FZ08U%2Fu%2B3BIviu4SGYdrl86sPrDvCiKeG%2Bg%3D%3D"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, blend_file_name)
    try:
        if os.path.isfile(dest_path) is not True:
            copy_from_network_drive()
        else:
            logging.info('Barbershop already downloaded')
    except Exception:
        logging.info("Could not copy barbershop blend file from network share")
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading barbershop scene from internet")
        response = requests.get(
            download_url, allow_redirects=True, timeout=120)
        with open(dest_path, 'wb') as file:
            file.write(response.content)


def time_to_seconds(time_string):
    """convert string to duration in seconds"""
    colon_count = time_string.count(':')
    time_format = "%H:%M:%S.%f"
    if colon_count < 2:
        time_format = "%M:%S.%f"
    time_obj = datetime.strptime(time_string, time_format)
    seconds = (time_obj.hour * 3600) + (time_obj.minute * 60) + time_obj.second + (time_obj.microsecond / 1e6)
    return seconds


def run_blender_render(executable_path: str, log_directory: str, device: str, benchmark: str) -> str:
    """Execute the blender render of barbershop, returns the duration as string"""
    blend_log = os.path.join(log_directory, "blender.log")
    root_dir = os.path.dirname(os.path.realpath(__file__))
    blend_path = os.path.join(root_dir, benchmark)
    cmd_line = f"\"{executable_path}\" -b -E CYCLES -y \"{blend_path}\" -f 1 -- --cycles-device {device} --cycles-print-stats"
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

