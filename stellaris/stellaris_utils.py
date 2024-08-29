"""Utility functions for Total War: Warhammer III test script"""
import os
import re
import sys
import logging
import shutil
import getpass
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

USERNAME = getpass.getuser()
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "stellaris.exe"
STEAM_GAME_ID = 281990
CONFIG_LOCATION = Path(f"C:\\Users\\{USERNAME}\\Documents\\Paradox Interactive\\Stellaris")
LOG_LOCATION = Path(f"C:\\Users\\{USERNAME}\\Documents\\Paradox Interactive\\Stellaris\\logs")
BENCHMARK_LOCATION = Path(f"C:\\Users\\{USERNAME}\\Documents\\Paradox Interactive\\Stellaris\\save games\\BENCHMARK")
CONFIG_FILENAME = "standard_settings.txt"
LOG_FILE = "game.log"


benchmark_files = [
    "benchmark.ini",
    "pdx_settings.txt",
    "standard_settings.txt"
]


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"		y=(\d+)")
    width_pattern = re.compile(r"		x=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


def find_score_in_log():
    """Reads score from local game log"""
    score_pattern = re.compile(r"Performance run took (\d+\.\d+)s")
    cfg = f"{LOG_LOCATION}\\{LOG_FILE}"
    score_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            score_match = score_pattern.search(line)
            if score_match is not None:
                score_value = score_match.group(1)
    return (score_value)


def copy_benchmarkfiles(benchmark_files: list[str]) -> None:
    """Copy benchmark config files to config directory"""
    for file in benchmark_files:
        try:
            src_path = SCRIPT_DIR / "settings" / file
            CONFIG_LOCATION.mkdir(parents=True, exist_ok=True)
            dest_path = CONFIG_LOCATION / file
            logging.info("copying: %s -> %s", src_path, dest_path)
            shutil.copy(src_path, dest_path)
        except OSError as ex:
            raise Exception("could not copy benchmark config files", cause=ex) from ex


def copy_save_from_network_drive(file_name, destination):
    """copy save file from network drive"""
    network_dir = Path("\\\\Labs\\labs\\03_ProcessingFiles\\Stellaris")
    source_path = network_dir.joinpath(file_name)
    logging.info("Copying %s from %s", file_name, source_path)
    shutil.copyfile(source_path, destination)


def delete_existing_saves():
    """delete existing save files"""
    BENCHMARK_LOCATION.mkdir(parents=True, exist_ok=True)
    files = os.listdir(BENCHMARK_LOCATION)
    if files is not None:
        try:
            for file in files:
                file_path = BENCHMARK_LOCATION.joinpath(file)
                if file_path.exists():
                    os.remove(file_path)
            logging.info(f"Removing any additional save files from {BENCHMARK_LOCATION}")
        except OSError as e:
            logging.error(f"Error occurred while deleting files: {e}")


def copy_benchmarksave() -> None:
    """Copy save game to saves directory"""
    try:
        benchmark_save = "August_28th_2024_Year2400.sav"
        copy_destination = SCRIPT_DIR.joinpath(benchmark_save)
        copy_save_from_network_drive(benchmark_save, copy_destination)
        config_dest = BENCHMARK_LOCATION / benchmark_save
        logging.info("Copying: %s -> %s", copy_destination, config_dest)
        shutil.copy(copy_destination, config_dest)
    except OSError as err:
        logging.error("Could not copy benchmark save game.")
        raise err
