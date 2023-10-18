
"""Blender render test script"""
import logging
import os
import re
import subprocess
import requests


def download_and_install_blender(url: str, msi_name: str):
    """Downloads blender msi"""
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, msi_name)
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading Blender MSI for installation")
        response = requests.get(url, allow_redirects=True, timeout=120)
        with open(dest_path, 'wb') as file:
            file.write(response.content)
    result = subprocess.run([f"MsiExec.exe /i {dest_path} ALLUSERS=1"], check=True)
    logging.info(result)

def download_barbershop_scene():
    """Downloads blender scene to render"""
    blend_file_name = "barbershop_interior.blend"
    download_url = f"https://svn.blender.org/svnroot/bf-blender/trunk/lib/benchmarks/cycles/barbershop_interior/{blend_file_name}"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dest_path = os.path.join(root_dir, blend_file_name)
    if os.path.isfile(dest_path) is not True:
        logging.info("Downloading barbershop scene")
        response = requests.get(
            download_url, allow_redirects=True, timeout=120)
        with open(dest_path, 'wb') as file:
            file.write(response.content)
    logging.info('Barbershop already downloaded')

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
    return time
