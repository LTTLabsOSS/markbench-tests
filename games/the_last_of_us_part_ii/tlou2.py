"""The Last of Us Part I test script"""

import logging
import shutil
import sys
import time
from importlib import import_module
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    create_artifacts_manifest,
)
from harness_utils.input import mangohud_log_toggle, press, user
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, network_drive_path, user_documents
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import (
    STEAMID64_ACCOUNT_ID_OFFSET,
    exec_steam_game,
    get_active_steam_account_id,
    get_proton_prefix,
)

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 2531310
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "tlou-ii.exe"

user.FAILSAFE = False


def reset_savedata(local_savegame_path):
    """
    Deletes the savegame folder from the local directory and replaces it with a new one from the network drive.
    """
    network_savegame_path = (
        network_drive_path()
        / "03_ProcessingFiles"
        / "The Last of Us Part II"
        / "savedata"
    )

    # Delete the local savedata folder if it exists
    if local_savegame_path.exists() and local_savegame_path.is_dir():
        shutil.rmtree(local_savegame_path)
        logger.info("Deleted local savedata folder: %s", local_savegame_path)

    # Copy the savedata folder from the network drive
    try:
        shutil.copytree(network_savegame_path, local_savegame_path)
        logger.info(
            "Copied savedata folder from %s to %s",
            network_savegame_path,
            local_savegame_path,
        )
    except Exception as e:
        logger.error("Failed to copy savedata folder: %s", e)

    # Check if the newly copied directory contains a folder called SAVEFILE0A


def delete_autosave(local_savegame_path):
    """
    Deletes the autosave folder from the local directory if it exists.
    """
    savefile_path = (
        local_savegame_path / "SAVEFILE0A"
    )  # check for autosaved file, delete if exists
    if savefile_path.exists() and savefile_path.is_dir():
        shutil.rmtree(savefile_path)
        logger.info("Deleted folder: %s", savefile_path)


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
    if is_linux():
        registry_path = get_proton_prefix(STEAM_GAME_ID) / "user.reg"
        escaped_key_path = key_path.replace("\\", "\\\\")
        section_prefix = f"[{escaped_key_path}]".casefold()
        value_prefix = f'"{value_name}"=dword:'.casefold()
        in_section = False

        try:
            with registry_path.open(encoding="utf-8") as registry_file:
                for line in registry_file:
                    line = line.strip()
                    if line.startswith("["):
                        in_section = line.casefold().startswith(section_prefix)
                    elif in_section and line.casefold().startswith(value_prefix):
                        return int(line.split(":", 1)[1], 16)
        except OSError as e:
            logger.error("Error reading registry value: %s", e)
            return None

        logger.error("Registry key not found: %s", value_name)
        return None

    winreg = import_module("winreg")
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        logger.error("Registry key not found: %s", value_name)
        return None
    except OSError as e:
        logger.error("Error reading registry value: %s", e)
        return None


def run_benchmark(local_savegame_path) -> tuple:
    """Starts Game, Sets Settings, and Runs Benchmark"""
    exec_steam_game(STEAM_GAME_ID)
    setup_start_time = int(time.time())

    if find_word("sony", timeout=60, interval=0.5) is None:
        logger.error("Couldn't find 'sony'")
    else:
        press("escape")

    if find_word("story", timeout=30, interval=1) is None:
        logger.error("Couldn't find main menu : 'story'")
        sys.exit(1)
    if is_linux():
        time.sleep(1)
        mangohud_log_toggle()
        time.sleep(1)
    press("down*2")

    # navigate settings
    navigate_settings()

    if find_word("story", timeout=5, interval=1) is None:
        logger.error("Couldn't find main menu the second time : 'story'")
        sys.exit(1)

    press("up*2, space*2")

    if find_word("continue", timeout=5, interval=1) is None:
        press("down")
    else:
        press("down*2")

    delete_autosave(local_savegame_path)

    time.sleep(0.3)

    press("space")

    if find_word("autosave", timeout=5, interval=1) is None:
        press("space")

    else:
        press("up, space")

    press("left, space")

    setup_end_time = test_start_time = test_end_time = int(time.time())

    elapsed_setup_time = setup_end_time - setup_start_time
    logger.info("Setup took %f seconds", elapsed_setup_time)

    # time of benchmark usually is 4:23 = 263 seconds

    if find_word("man", timeout=100) is not None:
        test_start_time = int(time.time()) - 14
        time.sleep(240)
    else:
        logger.error("couldn't find 'man'")
        time.sleep(150)

    if find_word("rush", timeout=100) is not None:
        time.sleep(3)
        test_end_time = int(time.time())
    else:
        logger.error("couldn't find 'rush', marks end of benchmark")
        test_end_time = int(time.time())

    elapsed_test_time = test_end_time - test_start_time
    logger.info("Test took %f seconds", elapsed_test_time)

    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


def navigate_settings() -> None:
    """Navigate through settings and take screenshots.
    Exits to main menu after taking screenshots.
    """

    press("space")

    if find_word("display", timeout=30, interval=1) is None:
        logger.error("Couldn't find display")
        sys.exit(1)

    time.sleep(5)  # slow cards may miss the first down

    press("down*4, space")

    if find_word("resolution", timeout=30, interval=1) is None:
        logger.error("Couldn't find resolution")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display1.png")

    press("up")

    if find_word("brightness", timeout=30, interval=1) is None:
        logger.error("Couldn't find brightness")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display2.png")

    press("q")  # swaps to graphics settings

    if find_word("preset", timeout=30, interval=1) is None:
        logger.error("Couldn't find preset")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics1.png")

    press("up")

    if find_word("dirt", timeout=30, interval=1) is None:
        logger.error("Couldn't find dirt")
        sys.exit(1)

    capture_and_save_screenshot(
        ARTIFACTS_DIRECTORY / "graphics3.png"
    )  # is at the bottom of the menu

    press("up*13")

    if find_word("scattering", timeout=30, interval=1) is None:
        logger.error("Couldn't find scattering")
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics2.png")

    press("escape*2")


def main():
    """Main function to run the benchmark"""
    try:
        logger.info("Starting The Last of Us Part II benchmark")

        steam_account_id = get_active_steam_account_id()
        steam_id64 = steam_account_id + STEAMID64_ACCOUNT_ID_OFFSET
        local_savegame_path = (
            user_documents(STEAM_GAME_ID)
            / "The Last of Us Part II"
            / str(steam_id64)
            / "savedata"
        )
        reset_savedata(local_savegame_path)

        start_time, end_time = run_benchmark(local_savegame_path)
        width, height = get_current_resolution()
        if width is None or height is None:
            logger.error("Could not read resolution")
            sys.exit(1)

        report = {
            "resolution": format_resolution(width, height),
            "start_time": seconds_to_milliseconds(
                start_time
            ),  # seconds to milliseconds
            "end_time": seconds_to_milliseconds(end_time),
        }
        write_report_json(LOG_DIRECTORY, "report.json", report)
        create_artifacts_manifest(ARTIFACTS_DIRECTORY)

    except Exception as e:
        logger.error("An error occurred: %s", e)
        logger.exception("Unhandled exception")
        terminate_process(PROCESS_NAME)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging(LOG_DIRECTORY)
    main()
