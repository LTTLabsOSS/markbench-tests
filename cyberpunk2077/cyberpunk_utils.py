"""Utility functions for Cyberpunk 2077 test script"""

import logging
import re
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)
from harness_utils.assets import resolve_asset
from harness_utils.paths import game_install_path, windows_local_appdata

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
STEAM_GAME_ID = 1091500
CYBERPUNK_ASSET_ENV_VAR = "MARKBENCH_CYBERPUNK_ASSET_DIR"
NO_INTRO_MOD_FILENAME = "basegame_no_intro_videos.archive"
NO_INTRO_MOD_NETWORK_PATH = Path(
    r"\\labs.lmg.gg\labs\03_ProcessingFiles\Cyberpunk 2077\basegame_no_intro_videos.archive"
)


def get_args():
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument(
        "--kerasHost",
        dest="keras_host",
        help="Host for Keras OCR service",
        required=True,
    )
    parser.add_argument(
        "--kerasPort",
        dest="keras_port",
        help="Port for Keras OCR service",
        required=True,
    )
    return parser.parse_args()


def copy_no_intro_mod() -> None:
    """Copies no intro mod file"""
    install_dir = game_install_path(STEAM_GAME_ID)
    mod_path = install_dir / "archive" / "pc" / "mod"
    mod_path.mkdir(parents=True, exist_ok=True)

    src_path = resolve_asset(
        SCRIPT_DIRECTORY / NO_INTRO_MOD_FILENAME,
        env_var=CYBERPUNK_ASSET_ENV_VAR,
        fallback_network_path=NO_INTRO_MOD_NETWORK_PATH,
    )
    dest_path = mod_path / NO_INTRO_MOD_FILENAME

    logging.info("Copying: %s -> %s", src_path, dest_path)
    if src_path.resolve() != dest_path.resolve():
        shutil.copy(src_path, dest_path)


def read_current_resolution():
    """Get resolution from local game file"""
    config_location = (
        windows_local_appdata(STEAM_GAME_ID)
        / "CD Projekt Red"
        / "Cyberpunk 2077"
    )
    config_path = config_location / "UserSettings.json"
    resolution_pattern = re.compile(r"\"value\"\: \"(\d+x\d+)\"\,")
    resolution = 0
    with open(config_path, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = resolution_match.group(1)
    return resolution
