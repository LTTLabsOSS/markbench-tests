"""The Last of Us Part I test script"""

import getpass
import logging
import shutil
import sys
import time
import winreg  # for accessing settings, including resolution, in the registry
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.input import press_n_times, user
from harness_utils.ocr_service import find_word
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_process
from harness_utils.steam import (
    exec_steam_run_command,
)

USERNAME = getpass.getuser()
STEAM_GAME_ID = 2531310
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "tlou-ii.exe"

user.FAILSAFE = False


def reset_savedata():
    """
    Deletes the savegame folder from the local directory and replaces it with a new one from the network drive.
    """
    local_savegame_path = Path(
        f"C:\\Users\\{USERNAME}\\Documents\\The Last of Us Part II\\76561199405246658\\savedata"
    )  # make this global
    network_savegame_path = Path(
        r"\\labs.lmg.gg\Labs\03_ProcessingFiles\The Last of Us Part II\savedata"
    )

    # Delete the local savedata folder if it exists
    if local_savegame_path.exists() and local_savegame_path.is_dir():
        shutil.rmtree(local_savegame_path)
        logging.info("Deleted local savedata folder: %s", local_savegame_path)

    # Copy the savedata folder from the network drive
    try:
        shutil.copytree(network_savegame_path, local_savegame_path)
        logging.info(
            "Copied savedata folder from %s to %s",
            network_savegame_path,
            local_savegame_path,
        )
    except Exception as e:
        logging.error("Failed to copy savedata folder: %s", e)

    # Check if the newly copied directory contains a folder called SAVEFILE0A


def delete_autosave():
    """
    Deletes the autosave folder from the local directory if it exists.
    """
    local_savegame_path = Path(
        f"C:\\Users\\{USERNAME}\\Documents\\The Last of Us Part II\\76561199405246658\\savedata"
    )
    savefile_path = (
        local_savegame_path / "SAVEFILE0A"
    )  # check for autosaved file, delete if exists
    if savefile_path.exists() and savefile_path.is_dir():
        shutil.rmtree(savefile_path)
        logging.info("Deleted folder: %s", savefile_path)


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


def run_benchmark() -> tuple:
    """Starts Game, Sets Settings, and Runs Benchmark"""
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    am = ArtifactManager(LOG_DIRECTORY)

    if find_word("sony", timeout=60, interval=0.2) is None:
        logging.error("Couldn't find 'sony'")
    else:
        user.press("escape")

    if find_word("story", timeout=30, interval=1) is None:
        logging.error("Couldn't find main menu : 'story'")
        sys.exit(1)

    press_n_times("down", 2)

    # navigate settings
    navigate_settings(am)

    if find_word("story", timeout=30, interval=1) is None:
        logging.error("Couldn't find main menu the second time : 'story'")
        sys.exit(1)

    press_n_times("up", 2)

    user.press("space")

    time.sleep(0.3)

    user.press("space")

    if find_word("continue", timeout=5, interval=0.2) is None:
        user.press("down")
    else:
        press_n_times("down", 2)

    delete_autosave()

    time.sleep(0.3)

    user.press("space")

    time.sleep(0.3)

    if find_word("autosave", timeout=5, interval=0.2) is None:
        user.press("space")

    else:
        user.press("up")

        time.sleep(0.3)

        user.press("space")

    time.sleep(0.3)

    user.press("left")

    time.sleep(0.3)

    user.press("space")

    setup_end_time = test_start_time = test_end_time = int(time.time())

    elapsed_setup_time = setup_end_time - setup_start_time
    logging.info("Setup took %f seconds", elapsed_setup_time)

    # time of benchmark usually is 4:23 = 263 seconds

    if find_word("man", timeout=100, interval=0.2) is not None:
        test_start_time = int(time.time()) - 14
        time.sleep(240)

    else:
        logging.error("couldn't find 'man'")
        time.sleep(150)

    if find_word("rush", timeout=100, interval=0.2) is not None:
        time.sleep(3)
        test_end_time = int(time.time())

    else:
        logging.error("couldn't find 'rush', marks end of benchmark")
        test_end_time = int(time.time())

    elapsed_test_time = test_end_time - test_start_time
    logging.info("Test took %f seconds", elapsed_test_time)

    terminate_process(PROCESS_NAME)

    am.create_manifest()

    return test_start_time, test_end_time


def navigate_settings(am: ArtifactManager) -> None:
    """Navigate through settings and take screenshots.
    Exits to main menu after taking screenshots.
    """

    user.press("space")

    if find_word("display", timeout=30, interval=1) is None:
        logging.error("Couldn't find display")
        sys.exit(1)

    time.sleep(5)  # slow cards may miss the first down

    press_n_times("down", 4)

    user.press("space")

    time.sleep(0.5)

    if find_word("resolution", timeout=30, interval=1) is None:
        logging.error("Couldn't find resolution")
        sys.exit(1)

    am.take_screenshot("display1.png", ArtifactType.CONFIG_IMAGE, "display settings 1")

    user.press("up")

    if find_word("brightness", timeout=30, interval=1) is None:
        logging.error("Couldn't find brightness")
        sys.exit(1)

    am.take_screenshot("display2.png", ArtifactType.CONFIG_IMAGE, "display settings 2")

    user.press("q")  # swaps to graphics settings

    time.sleep(0.5)

    if find_word("preset", timeout=30, interval=1) is None:
        logging.error("Couldn't find preset")
        sys.exit(1)

    am.take_screenshot(
        "graphics1.png", ArtifactType.CONFIG_IMAGE, "graphics settings 1"
    )

    user.press("up")

    if find_word("dirt", timeout=30, interval=1) is None:
        logging.error("Couldn't find dirt")
        sys.exit(1)

    am.take_screenshot(
        "graphics3.png", ArtifactType.CONFIG_IMAGE, "graphics settings 3"
    )  # is at the bottom of the menu

    press_n_times("up", 13)

    if find_word("scattering", timeout=30, interval=1) is None:
        logging.error("Couldn't find scattering")
        sys.exit(1)

    am.take_screenshot(
        "graphics2.png", ArtifactType.CONFIG_IMAGE, "graphics settings 2"
    )

    press_n_times("escape", 2)


def main():
    """Main function to run the benchmark"""
    try:
        logging.info("Starting The Last of Us Part II benchmark")

        reset_savedata()

        start_time, end_time = run_benchmark()
        width, height = get_current_resolution()
        if width is None or height is None:
            logging.error("Could not read resolution")
            sys.exit(1)

        report = {
            "resolution": format_resolution(width, height),
            "start_time": seconds_to_milliseconds(
                start_time
            ),  # seconds to milliseconds
            "end_time": seconds_to_milliseconds(end_time),
        }
        write_report_json(LOG_DIRECTORY, "report.json", report)

    except Exception as e:
        logging.error("An error occurred: %s", e)
        logging.exception(e)
        terminate_process(PROCESS_NAME)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging(LOG_DIRECTORY)
    main()
