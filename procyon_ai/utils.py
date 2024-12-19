"""3dmark test utils"""
from pathlib import Path
import psutil
import xml.etree.ElementTree as ET
import winreg
import re
import subprocess

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"

def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process
    return None

def find_score_in_xml():
    """Reads score from local game log"""
    score_pattern = re.compile(r"<AIOverallScore>(\d+)")
    cfg = f"{LOG_DIR}\\result.xml"
    score_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            score_match = score_pattern.search(line)
            if score_match is not None:
                score_value = score_match.group(1)
    return score_value

def get_install_path() -> str:
    """Gets the path to the Steam installation directory from the SteamPath registry key"""
    reg_path = r"Software\UL\Procyon"
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    value, _  = winreg.QueryValueEx(reg_key, "InstallDir")
    return value

def get_winml_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available winml devices on the system. Returns a dictionary of device names and IDs
    """

    # run the command line utility for procyon in order to list available winml devices
    winml_devices = subprocess.run([f'{procyon_path}', '--list-winml-devices'], shell=True, capture_output=True, text=True, check=True).stdout

    winml_devices_split = winml_devices.split('\n')
    winml_devices_parsed = [device[9::] for device in winml_devices_split if re.search(r"(amd|nvidia|intel)", device.lower())]
    unique_winml_devices = list(dict.fromkeys(winml_devices_parsed))
    winml_dict = {device_split.split(', ')[0]:device_split.split(', ')[1] for device_split in unique_winml_devices}

    return winml_dict
