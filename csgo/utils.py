"""Utility functions for CS:GO test script"""
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

import requests

sys.path.insert(1, os.path.join(sys.path[0], ".."))

# pylint: disable=wrong-import-position
from harness_utils.steam import (
    get_app_install_location,
    get_registry_active_user,
    get_steam_folder_path,
)

# pylint: enable=wrong-import-position

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
BENCHMARK_PATH = SCRIPT_DIRECTORY.joinpath("csgo-benchmark-master", "csgo")
ZIP_NAME = "csgo-benchmark-master.zip"
ZIP_PATH = SCRIPT_DIRECTORY.joinpath(ZIP_NAME)

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
STEAM_GAME_ID = 730
CSGO_BENCHMARK_PATH = os.path.join(SCRIPT_DIRECTORY, "csgo-benchmark-master", "csgo")
CSGO_BENCHMARK_ZIP_NAME = "csgo-benchmark-master.zip"


def get_resolution():
    """Gets the resolution from a local file"""
    height_pattern = re.compile(r"\"setting.defaultresheight\"		\"(\d+)\"")
    width_pattern = re.compile(r"\"setting.defaultres\"		\"(\d+)\"")
    steam_path = get_steam_folder_path()
    user_id = get_registry_active_user()
    config_path = Path(steam_path).joinpath(
        "userdata", user_id, STEAM_GAME_ID, "local", "cfg", "video.txt"
    )

    height = 0
    width = 0
    with open(config_path, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)


def benchmark_folder_exists() -> bool:
    """Check if the CSGO Benchmark has been downloaded or not"""
    return BENCHMARK_PATH.is_dir()


def download_benchmark():
    """Downloads and extracts the CSGO Benchmark scripts"""
    download_url = (
        "https://github.com/samisalreadytaken/csgo-benchmark/archive/master.zip"
    )
    logging.info("Downloading and extracting benchmark to %s", SCRIPT_DIRECTORY)

    if not ZIP_PATH.exists():
        response = requests.get(download_url, allow_redirects=True, timeout=180)
        with open(ZIP_PATH, "wb") as file:
            file.write(response.content)

    with ZipFile(ZIP_PATH, "r") as zip_object:
        zip_object.extractall(path=SCRIPT_DIRECTORY)


def copy_benchmark():
    """Copies the downloaded benchmark to the CSGO directory"""
    dest_dir = Path(get_app_install_location(STEAM_GAME_ID)).joinpath("csgo")
    logging.info("Copying benchmark from %s to %s", BENCHMARK_PATH, dest_dir)
    shutil.copytree(BENCHMARK_PATH, dest_dir, dirs_exist_ok=True)
