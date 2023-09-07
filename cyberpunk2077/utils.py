from argparse import ArgumentParser
import os
import logging
from pathlib import Path
import re
import shutil

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
CYBERPUNK_INSTALL_DIR = os.path.join(
    os.environ["ProgramFiles(x86)"], "Steam\steamapps\common\Cyberpunk 2077")
DEFAULT_NO_INTRO_PATH = os.path.join(CYBERPUNK_INSTALL_DIR, "archive\pc\mod")


def get_args() -> any:
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()


def copy_no_intro_mod() -> None:
    src_file = os.path.join(
        SCRIPT_DIRECTORY, "basegame_no_intro_videos.archive")
    is_valid_no_intro = os.path.isfile(src_file)

    if not is_valid_no_intro:
        raise Exception(f"Can't find no intro: {src_file}")

    # Validate/create path to directory where we will copy profile to
    dest_dir: str = DEFAULT_NO_INTRO_PATH
    try:
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error(
            "Could not create rtss profiles directory - likely due to non-directory file existing at path.")
        raise e

    # Copy the profile over
    destination_file = os.path.join(dest_dir, os.path.basename(src_file))
    logging.info(F"Copying: {src_file} -> {destination_file}")
    shutil.copy(src_file, destination_file)


def read_current_resolution():
    APPDATA = os.getenv("LOCALAPPDATA")
    CONFIG_LOCATION = f"{APPDATA}\\CD Projekt Red\\Cyberpunk 2077"
    CONFIG_FILENAME = "UserSettings.json"
    resolution_pattern = re.compile(r"\"value\"\: \"(\d+x\d+)\"\,")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    resolution = 0
    with open(cfg) as f:
        lines = f.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = resolution_match.group(1)
    return (resolution)
