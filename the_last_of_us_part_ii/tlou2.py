"""The Last of Us Part I test script"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import time
import sys
import pydirectinput as user

import winreg  # for accessing settings, including resolution, in the registry

import shutil

sys.path.insert(1, str(Path(sys.path[0]).parent))

from harness_utils.keras_service import KerasService
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
    setup_logging,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    exec_steam_run_command,
)

from harness_utils.artifacts import ArtifactManager, ArtifactType

from harness_utils.misc import int_time, find_word, press_n_times


STEAM_GAME_ID = 2531310
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "tlou-ii.exe"

user.FAILSAFE = False


def reset_savedata():
    """
    Deletes the savegame folder from the local directory and replaces it with a new one from the network drive.
    """
    local_savegame_path = Path(r"C:\Users\Administrator\Documents\The Last of Us Part II\76561199405246658\savedata")
    network_savegame_path = Path(r"\\Labs\Labs\03_ProcessingFiles\The Last of Us Part II\savedata")

    # Delete the local savedata folder if it exists
    if local_savegame_path.exists() and local_savegame_path.is_dir():
        shutil.rmtree(local_savegame_path)
        logging.info("Deleted local savedata folder: %s", local_savegame_path)

    # Copy the savedata folder from the network drive
    try:
        shutil.copytree(network_savegame_path, local_savegame_path)
        logging.info("Copied savedata folder from %s to %s", network_savegame_path, local_savegame_path)
    except Exception as e:
        logging.error("Failed to copy savedata folder: %s", e)


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
    """
    Reads value from registry
        A helper function for get_current_resolution
    """
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
    """Starts Game, Sets Settings, and Runs Benchmark"""
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int_time()
    am = ArtifactManager(LOG_DIRECTORY)

    if keras_service.wait_for_word(word="sony", timeout=60, interval=0.2) is None:
        logging.error("Couldn't find 'sony'")
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
        test_start_time = int_time() - 60

    time.sleep(240)

    if keras_service.wait_for_word(word="rush", timeout=100, interval=0.2) is None:
        logging.error("couldn't find 'rush', marks end of benchmark")
        test_end_time = int_time() + 3
    else:
        test_end_time = int_time()

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
    """Main function to run the benchmark"""
    try:
        logging.info("Starting The Last of Us Part II benchmark")
        parser = ArgumentParser()
        parser.add_argument("--kerasHost", dest="keras_host",
                            help="Host for Keras OCR service", required=True)
        parser.add_argument("--kerasPort", dest="keras_port",
                            help="Port for Keras OCR service", required=True)
        args = parser.parse_args()
        keras_service = KerasService(args.keras_host, args.keras_port)

        reset_savedata()

        start_time, end_time = run_benchmark(keras_service)
        resolution_tuple = get_current_resolution()
        report = {
            "resolution": format_resolution(resolution_tuple[0], resolution_tuple[1]),
            "start_time": seconds_to_milliseconds(start_time),  # secconds to miliseconds
            "end_time": seconds_to_milliseconds(end_time),
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
