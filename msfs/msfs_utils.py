"""Utility functions for Microsoft Flight Simulator 2020 test script"""
import os
import re
import sys
import logging
import shutil
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = Path(f"{APPDATA}\\Microsoft Flight Simulator")
CONFIG_FILENAME = "UserCfg.opt"

def read_current_resolution():
    """Reads resolutions settings from local game file"""
    resolution_pattern = re.compile(r"FullScreenResolution (\d+ \d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    resolution = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = re.sub(r"\s", "x", resolution_match.group(1))
    return resolution


def copy_flight(flight_files: list[str]) -> None:
    """Copy benchmark config files to config directory"""
    for file in flight_files:
        try:
            src_path = SCRIPT_DIRECTORY / file
            CONFIG_LOCATION.mkdir(parents=True, exist_ok=True)

            dest_path = CONFIG_LOCATION / file
            logging.info("Copying: %s -> %s", src_path, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as err:
            logging.error("Could not copy benchmark config files.")
            raise err
        
def copy_mod_to_harness():
    """Copy Plane Mod from Labs Drive"""
    source = Path("\\\\labs\\labs\\03_ProcessingFiles\\MSFS2020\\PlaneMod\\Bonanza-Turbo-V4-1SU6")
    destination = Path(f"{SCRIPT_DIRECTORY}\\Bonanza-Turbo-V4-1SU6")
    if not os.path.exists(destination):
        shutil.copytree(source, destination, dirs_exist_ok=True)
        logging.info(f"Copying mod to {destination}")
    else:
        logging.info("Mod already copied to harness folder.")

def install_mod():
    """Copy Plane Mod to mod folder"""
    copy_mod_to_harness()
    source = Path(f"{SCRIPT_DIRECTORY}\\Bonanza-Turbo-V4-1SU6")
    destination = Path(f"{CONFIG_LOCATION}\\Packages\\Community\\Bonanza-Turbo-V4-1SU6")
    if not os.path.exists(destination):
        shutil.copytree(source, destination, dirs_exist_ok=True)
        logging.info(f"Installing mod to {destination}")
    else:
        logging.info("Mod already installed.")