"""The Last of Us Part I test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import re
import pydirectinput as user

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.keras_service import KerasService
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    get_registry_active_user,
    exec_steam_run_command,
)

from harness_utils.artifacts import ArtifactManager, ArtifactType

STEAM_GAME_ID = 2531310
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")

user.FAILSAFE = False


def setup_logging():
    setup_log_directory(LOG_DIRECTORY)

    logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"FullscreenWidth=(\d+)")
    width_pattern = re.compile(r"FullscreenHeight=(\d+)")
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

def run_benchmark(keras_service: KerasService) -> tuple:
    return (0,0)

def main():
    """entry point"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    keras_service = KerasService(args.keras_host, args.keras_port)
    start_time, endtime = run_benchmark(keras_service)