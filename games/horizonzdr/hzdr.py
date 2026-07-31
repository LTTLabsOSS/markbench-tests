"""Horizon Zero Dawn Remastered test script"""

import logging
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.file_cleanup import remove_files
from harness_utils.input import mangohud_log_toggle, press
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.registry import RegistryEntry, read_registry_key, read_registry_value
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import (
    exec_steam_run_command,
    get_build_id,
    get_steamapps_common_path,
)

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 2561580
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "HorizonZeroDawnRemastered.exe"
VIDEO_PATH = (
    get_steamapps_common_path() / "Horizon Zero Dawn Remastered" / "Movies" / "Mono"
)
CONFIG_FILE = SCRIPT_DIRECTORY / "graphics_config.txt"
SUBKEY = r"SOFTWARE\Guerrilla Games\Horizon Zero Dawn Remastered\Graphics"

intro_videos = [
    VIDEO_PATH / "weaseltron_logo.bk2",
    VIDEO_PATH / "sony_studios_reel.bk2",
    VIDEO_PATH / "nixxes_logo.bk2",
    VIDEO_PATH / "Logo.bk2",
    VIDEO_PATH / "guerilla_logo.bk2",
]


def process_registry_file(
    registry_values: dict[str, RegistryEntry],
    subkey: str,
    config_file: str | Path,
) -> None:
    """Write registry values to a readable graphics configuration file."""
    lines = ["Windows Registry Editor Version 5.00\n", "\n", f"[{subkey}]\n"]

    for value_name, entry in registry_values.items():
        if entry.kind == "dword":
            value_data = str(entry.value)
        elif entry.kind == "qword":
            value_data = f"qword:{entry.value:016x}"
        else:
            escaped_value = str(entry.value).replace("\\", "\\\\").replace('"', '\\"')
            value_data = f'"{escaped_value}"'
        lines.append(f'"{value_name}"={value_data}\n')

    with open(config_file, "w", encoding="utf-8") as file:
        file.writelines(lines)


def run_benchmark() -> tuple[int, int]:
    """Run the benchmark"""
    logger.info("Removing intro videos")
    remove_files([str(path) for path in intro_videos])

    logger.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())

    time.sleep(10)
    # skip intro
    press("esc")
    # Make sure the game started correctly
    if find_word(word="quit", timeout=30, interval=1) is None:
        logger.info("Could not find the main menu. Did the game load?")
        sys.exit(1)

    if is_linux():
        mangohud_log_toggle()

    # Navigate to options menu
    press("down*2, enter")

    if find_word(word="language", timeout=30, interval=1) is None:
        logger.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    press("e")

    # Verify that we have navigated to the display settings menu and take a screenshot
    if find_word(word="monitor", timeout=30, interval=1) is None:
        logger.info("Did not find the display settings menu. Did the menu get stuck?")
        sys.exit(1)
    # Check if its fullscreen only and not exclusive fullscreen
    if find_word(word="exclusive", timeout=3, interval=0.5) is None:
        press("down, right, up, r")
        # Resets focus to first position before applying settings
        press("enter", pause=1)
        press("enter")
    # Checks frame rate setting, sometimes this can be incorrect even if it is set to exclusive fullscreen
    if find_word(word="144", timeout=3, interval=0.5) is None:
        press("down")
        # Sometimes when the screen refreshes if the setting is changed from fullscreen to exclusive, the cursor highlights on v-sync because technically it moves it to the center so the game picks that up as a focusing movement.
        # This checks if we are in the proper position by going down one and seeing if we can see 'generation' from frame generation, which should not be visible if we are in the correct focus location
        # Either position once known is routed to the correct position via this if/else statement
        if find_word(word="generation", timeout=3, interval=0.5):
            press("up*2")
        else:
            press("down*5, right")
        # This while loop is for the case when we switch to exclusive fullscreen from fullscreen, occasionally it will set to 30Hz, we want to get to 144Hz
        # So we should be highlighted on refresh rate at this point, it will (if not 144) do the first press("right") then check for 144, if not present it will continue pressing right and checking after for 144
        # This solves arbitrary steps to get to 144Hz, and sets us up if we want to alter that target hz setting we can just change the word variable below.
        # KNOWN LIMITATION  we can maybe pull the max refresh some other way if we care about whether the display is not 144Hz max, so as to handle all edge cases here.
        while find_word(word="144", timeout=1, interval=0.5) is None:
            press("right")
        # Apply Hz setting once it is correct, then go up one so the proper settings are in view for the screenshot
        press("r")
        press("enter", pause=1)
        press("enter, up*6")
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display1.png")

    press("up")

    if find_word(word="upscale", timeout=30, interval=1) is None:
        logger.info("Did not find the upscale settings. Did the menu not scroll?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display2.png")

    # Navigate to graphics menu
    press("e")

    if find_word(word="preset", timeout=30, interval=1) is None:
        logger.info("Did not find the graphics settings menu. Did the menu get stuck?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics1.png")

    press("up")

    if find_word(word="sharpness", timeout=30, interval=1) is None:
        logger.info("Did not find the sharpness settings. Did the menu not scroll?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics2.png")

    # Launch the benchmark
    press("tab, enter")

    setup_end_time = int(time.time())
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logger.info("Setup took %s seconds", elapsed_setup_time)

    if find_word(word="continue", timeout=120, interval=1) is None:
        logger.info(
            "Did not find the continue button. Did the game not finish loading?"
        )
        sys.exit(1)

    press("enter")

    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(180)

    # Wait for results screen to display info
    if find_word(word="results", timeout=20, interval=0.5) is None:
        logger.info(
            "Did not find the results screen. Did the game not finish the benchmark?"
        )
        sys.exit(1)

    test_end_time = round(int(time.time()))
    # Give results screen time to fill out, then save screenshot and config file
    time.sleep(2)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    registry_values = read_registry_key(SUBKEY, steam_app_id=STEAM_GAME_ID)
    process_registry_file(registry_values, SUBKEY, CONFIG_FILE)
    copy_artifact(CONFIG_FILE, ARTIFACTS_DIRECTORY)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logger.info("Benchmark took %s seconds", elapsed_test_time)

    terminate_process(PROCESS_NAME)

    time.sleep(15)
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    width = read_registry_value(SUBKEY, "FullscreenWidth", steam_app_id=STEAM_GAME_ID)
    height = read_registry_value(SUBKEY, "FullscreenHeight", steam_app_id=STEAM_GAME_ID)
    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("Could not read resolution from the registry")

    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    terminate_process(PROCESS_NAME)
    sys.exit(1)
