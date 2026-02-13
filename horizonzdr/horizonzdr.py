"""Horizon Zero Dawn Remastered test script"""

import logging
import os
import sys
import time
import winreg

from horizonzdr_utils import get_resolution, get_args, process_registry_file

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import KerasService
from harness_utils.misc import remove_files
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    exec_steam_run_command,
    get_build_id,
    get_steamapps_common_path,
)

STEAM_GAME_ID = 2561580
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "HorizonZeroDawnRemastered"
VIDEO_PATH = os.path.join(
    get_steamapps_common_path(), "Horizon Zero Dawn Remastered", "Movies", "Mono"
)
input_file = os.path.join(SCRIPT_DIRECTORY, "graphics.reg")
config_file = os.path.join(SCRIPT_DIRECTORY, "graphics_config.txt")
hive = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\\Guerrilla Games\\Horizon Zero Dawn Remastered\\Graphics"

user.FAILSAFE = False

intro_videos = [
    os.path.join(VIDEO_PATH, "weaseltron_logo.bk2"),
    os.path.join(VIDEO_PATH, "sony_studios_reel.bk2"),
    os.path.join(VIDEO_PATH, "nixxes_logo.bk2"),
    os.path.join(VIDEO_PATH, "Logo.bk2"),
    os.path.join(VIDEO_PATH, "guerilla_logo.bk2"),
]


def run_benchmark() -> tuple[float]:
    """Run the benchmark"""
    logging.info("Removing intro videos")
    remove_files(intro_videos)

    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    am = ArtifactManager(LOG_DIRECTORY)

    time.sleep(10)

    # Make sure the game started correctly
    if kerasService.wait_for_word(word="quit", timeout=30, interval=1) is None:
        logging.info("Could not find the main menu. Did the game load?")
        sys.exit(1)

    # Navigate to options menu
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(0.5)

    if kerasService.wait_for_word(word="language", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    user.press("e")
    time.sleep(0.5)

    # Verify that we have navigated to the display settings menu and take a screenshot
    if kerasService.wait_for_word(word="monitor", timeout=30, interval=1) is None:
        logging.info("Did not find the display settings menu. Did the menu get stuck?")
        sys.exit(1)
    am.take_screenshot(
        "display1.png", ArtifactType.CONFIG_IMAGE, "1st picture of display settings"
    )

    user.press("up")
    time.sleep(0.5)

    if kerasService.wait_for_word(word="upscale", timeout=30, interval=1) is None:
        logging.info("Did not find the upscale settings. Did the menu not scroll?")
        sys.exit(1)
    am.take_screenshot(
        "display2.png", ArtifactType.CONFIG_IMAGE, "2nd picture of display settings"
    )

    # Navigate to graphics menu
    user.press("e")
    time.sleep(0.5)

    if kerasService.wait_for_word(word="preset", timeout=30, interval=1) is None:
        logging.info("Did not find the graphics settings menu. Did the menu get stuck?")
        sys.exit(1)
    am.take_screenshot(
        "graphics1.png", ArtifactType.CONFIG_IMAGE, "1st picture of graphics settings"
    )

    user.press("up")
    time.sleep(0.5)

    if kerasService.wait_for_word(word="sharpness", timeout=30, interval=1) is None:
        logging.info("Did not find the sharpness settings. Did the menu not scroll?")
        sys.exit(1)
    am.take_screenshot(
        "graphics2.png", ArtifactType.CONFIG_IMAGE, "2nd picture of graphics settings"
    )

    # Launch the benchmark
    user.press("tab")
    time.sleep(0.5)
    user.press("enter")

    setup_end_time = int(time.time())
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logging.info("Setup took %s seconds", elapsed_setup_time)

    if kerasService.wait_for_word(word="continue", timeout=120, interval=1) is None:
        logging.info(
            "Did not find the continue button. Did the game not finish loading?"
        )
        sys.exit(1)

    user.press("enter")

    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(180)

    # Wait for results screen to display info
    if kerasService.wait_for_word(word="results", timeout=20, interval=0.1) is None:
        logging.info(
            "Did not find the results screen. Did the game not finish the benchmark?"
        )
        sys.exit(1)

    test_end_time = round(int(time.time()))
    # Give results screen time to fill out, then save screenshot and config file
    time.sleep(2)
    am.take_screenshot(
        "result.png", ArtifactType.RESULTS_IMAGE, "screenshot of benchmark result"
    )
    process_registry_file(hive, SUBKEY, input_file, config_file)
    am.copy_file(config_file, ArtifactType.CONFIG_TEXT, "config file")

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %s seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)
    am.create_manifest()
    time.sleep(15)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(
    filename=f"{LOG_DIRECTORY}/harness.log",
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG,
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

args = get_args()
kerasService = KerasService(args.keras_host, args.keras_port)

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution(config_file)
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
