"""Utility functions supporting Doom: The Dark Ages test script."""
import os
import re
from pathlib import Path
import sys
import logging
import shutil
import json

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from harness_utils.steam import get_app_install_location

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
RUN_DIR = SCRIPT_DIRECTORY / "run"
STEAM_GAME_ID = 3017860
username = os.getlogin()
BENCHMARK_PATH = f"C:\\Users\\{username}\\Saved Games\\id Software\\DOOMTheDarkAges\\base\\benchmark"
RES_REGEX = re.compile(r'\s*(\d+)\s*[x×]\s*(\d+)')

def get_resolution() -> tuple[int, int]:
    """Gets resolution width and height from local xml file created by game."""
    try:
        bench_file = max(
            RUN_DIR.glob("benchmark-*.json"),
            key=lambda p: p.stat().st_mtime
        )
    except ValueError:
        raise FileNotFoundError(f"No benchmark-*.json files in {RUN_DIR}")

    with bench_file.open(encoding="utf-8") as f:
        data = json.load(f)

    res_string = data.get("resolution", "")
    m = RES_REGEX.search(res_string)
    if not m:
        raise ValueError(
            f"Cannot parse 'resolution' in {bench_file.name}: {res_string!r}"
        )

    width, height = map(int, m.groups())
    return width, height

def copy_launcher_config() -> None:
    """Copy launcher config to doom launcher config folder"""
    try:
        launcherconfig_path = Path(get_app_install_location(STEAM_GAME_ID), "launcherData\\base\\configs")
        launcherconfig_path.mkdir(parents=True, exist_ok=True)

        src_path = SCRIPT_DIRECTORY / "launcher.cfg"
        dest_path = launcherconfig_path / "launcher.cfg"

        logging.info("Copying: %s -> %s", src_path, dest_path)
        shutil.copy(src_path, dest_path)
    except OSError as err:
        logging.error("Could not copy config file.")
        raise err
    
