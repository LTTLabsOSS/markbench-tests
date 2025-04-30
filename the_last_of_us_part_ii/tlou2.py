"""The Last of Us Part I test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import re
import pydirectinput as user

import winreg

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

def get_current_resolution():
    """Reads resolutions settings from registry"""
    key_path = r"SOFTWARE\NaughtyDog\The Last of Us Part II\Graphics"
    fullscreen_width = read_registry_value(key_path, "FullscreenWidth")
    fullscreen_height = read_registry_value(key_path, "FullscreenHeight")

    return (fullscreen_height, fullscreen_width)    
    

def read_registry_value(key_path, value_name):
    """Reads resolutions settings from registry"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "WindowedResolution")
            return value
    except FileNotFoundError:
        logging.error("Registry key not found: %s", value_name)
        return None
    except OSError as e:
        logging.error("Error reading registry value: %s", e)
        return None
    

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
    print(get_current_resolution())
    start_time, endtime = run_benchmark(keras_service)