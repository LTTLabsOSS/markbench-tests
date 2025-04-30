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
    write_report_json,
    setup_logging,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    get_registry_active_user,
    exec_steam_run_command,
)

from harness_utils.artifacts import ArtifactManager, ArtifactType

from harness_utils.misc import int_time, find_word, press_n_times

STEAM_GAME_ID = 2531310
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "tlou-ii.exe"

user.FAILSAFE = False


def get_current_resolution():
    """
    Returns:
        tuple: (width, height)
    Reads resolutions settings from registry
    """
    key_path = r"Software\Naughty Dog\The Last of Us Part II\Graphics"
    fullscreen_width = read_registry_value(key_path, "FullscreenWidth")
    fullscreen_height = read_registry_value(key_path, "FullscreenHeight")

    return (fullscreen_width, fullscreen_height)


def read_registry_value(key_path, value_name):
    """Reads resolutions settings from registry"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        logging.error("Registry key not found: %s", value_name)
        return None
    except OSError as e:
        logging.error("Error reading registry value: %s", e)
        return None


def run_benchmark(keras_service: KerasService) -> tuple:
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int_time()
    am = ArtifactManager(LOG_DIRECTORY)
    time.sleep(20)

    if keras_service.wait_for_word(word="sony", timeout=30, interval=0.5) is None:
        logging.error("couldn't find 'sony'")
    else:
        user.press("escape")

    find_word(keras_service, "story", "Couldn't find main menu : 'story'")

    press_n_times("down", 2)

    # navigate settings
    navigate_settings(am)

    press_n_times("up", 2)

    user.press("space")

    user.press("down")

    user.press("space")

    user.press("space")

    user.press("left")

    user.press("space")

    setup_end_time = int_time()
    elapsed_setup_time = setup_end_time - setup_start_time
    logging.info("Setup took %f seconds", elapsed_setup_time)

    test_start_time = int_time()

    if keras_service.wait_for_word(word="man", timeout=60, interval=0.2) is None:
        logging.error("couldn't find 'man'")
    else:
        test_start_time = int_time() - 15

    time.sleep(260)

    if keras_service.wait_for_word(word="ellie", timeout=60, interval=0.2) is None:
        logging.error("couldn't find 'ellie'")
        test_end_time = int_time()
    else:
        test_end_time = int_time() - 10

    elapsed_test_time = test_end_time - test_start_time
    logging.info("Test took %f seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)

    am.create_manifest()

    return test_start_time, test_end_time


def navigate_settings(am: ArtifactManager) -> None:
    """Navigate through settings and take screenshots. 
    Exits to main menu after taking screenshots.
    """

    user.press("space")

    press_n_times("down", 4)

    user.press("space")

    time.sleep(0.5)

    am.take_screenshot("display1.png", ArtifactType.CONFIG_IMAGE, "display settings 1")

    user.press("up")

    am.take_screenshot("display2.png", ArtifactType.CONFIG_IMAGE, "display settings 2")

    user.press("q")  # swaps to graphics settings

    time.sleep(0.5)

    am.take_screenshot("graphics1.png", ArtifactType.CONFIG_IMAGE, "graphics settings 1")

    user.press("up")

    am.take_screenshot("graphics3.png", ArtifactType.CONFIG_IMAGE,
                       "graphics settings 3")  # is at the bottom of the menu

    press_n_times("up", 12)

    am.take_screenshot("graphics2.png", ArtifactType.CONFIG_IMAGE, "graphics settings 2")

    press_n_times("escape", 2)


def main():
    try:
        logging.info("Starting The Last of Us Part II benchmark")
        parser = ArgumentParser()
        parser.add_argument("--kerasHost", dest="keras_host",
                            help="Host for Keras OCR service", required=True)
        parser.add_argument("--kerasPort", dest="keras_port",
                            help="Port for Keras OCR service", required=True)
        args = parser.parse_args()
        keras_service = KerasService(args.keras_host, args.keras_port)

        start_time, end_time = run_benchmark(keras_service)
        resolution_tuple = get_current_resolution()
        report = {
            "resolution": format_resolution(resolution_tuple[0], resolution_tuple[1]),
            "start_time": start_time,
            "end_time": end_time,
        }
        write_report_json(LOG_DIRECTORY, "report.json", report)
        
    except Exception as e:
        logging.error("An error occurred: %s", e)
        logging.exception(e)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)

if __name__ == "__main__":
    setup_logging(LOG_DIRECTORY)
    main()
