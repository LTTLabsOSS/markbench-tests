"""Returnal test script"""

import logging
import os
import sys
import time
from pathlib import Path

import pydirectinput as user
from returnal_utils import get_args, get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import KerasService
from harness_utils.misc import press_n_times, remove_files
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    exec_steam_run_command,
    get_build_id,
    get_steamapps_common_path,
)

STEAM_GAME_ID = 1649240
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "Returnal"
LOCAL_USER_SETTINGS = (
    Path(os.getenv("LOCALAPPDATA"))
    / "Returnal"
    / "Steam"
    / "Saved"
    / "Config"
    / "WindowsNoEditor"
    / "GameUserSettings.ini"
)
VIDEO_PATH = (
    Path(get_steamapps_common_path()) / "Returnal" / "Returnal" / "Content" / "Movies"
)

user.FAILSAFE = False

intro_videos = [
    VIDEO_PATH / "Logos_PC.mp4",
    VIDEO_PATH / "Logos_PC_UW21.mp4",
    VIDEO_PATH / "Logos_PC_UW32.mp4",
    VIDEO_PATH / "Logos_Short_PC.mp4",
    VIDEO_PATH / "Logos_Short_PC_UW21.mp4",
    VIDEO_PATH / "Logos_Short_PC_UW32.mp4",
]


def check_vram_alert(attempts: int) -> bool:
    """Look for VRAM alert in menu"""
    logging.info("Checking for VRAM alert prompt")
    for _ in range(attempts):
        alert_result = kerasService.look_for_word("alert")
        locate_result = kerasService.look_for_word("locate")
        if locate_result is not None:
            return False
        if alert_result is not None:
            return True
        time.sleep(2)

    return False


def escape_vram_alert():
    """Navigate VRAM alert"""
    user.keyDown("space")
    time.sleep(4)
    user.keyUp("space")


def navigate_options_menu() -> None:
    """Simulate inputs to navigate to options menu"""
    logging.info("Navigating to options menu")
    user.press("esc")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)
    user.press("q")
    time.sleep(0.2)
    user.keyDown("tab")
    time.sleep(5)
    user.keyUp("tab")


def run_benchmark() -> tuple[float]:
    """Run the benchmark"""
    logging.info("Removing intro videos")
    remove_files([str(path) for path in intro_videos])

    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    am = ArtifactManager(LOG_DIRECTORY)

    time.sleep(10)

    # Check if GPU has too little v ram and skip alert
    alert_found = check_vram_alert(7)

    if alert_found:
        escape_vram_alert()

    # Make sure the game started correctly
    result = kerasService.look_for_word("locate", 10, 5)
    if not result:
        logging.info("Could not find prompt to open menu!")
        sys.exit(1)

    # Navigate to display menu
    user.press("esc")
    time.sleep(1)
    user.press("enter")
    time.sleep(1)
    user.press("q")
    time.sleep(1)
    user.press("q")
    time.sleep(1)

    # Verify that we have navigated to the video settings menu and take a screenshot
    if kerasService.wait_for_word(word="aspect", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)
    am.take_screenshot(
        "video.png", ArtifactType.CONFIG_IMAGE, "picture of video settings"
    )

    # Navigate to graphics menu
    user.press("e")
    time.sleep(1)

    if kerasService.wait_for_word(word="vsync", timeout=30, interval=1) is None:
        logging.info("Did not find the graphics settings menu. Did the menu get stuck?")
        sys.exit(1)
    am.take_screenshot(
        "graphics_1.png",
        ArtifactType.CONFIG_IMAGE,
        "first picture of graphics settings",
    )

    # We check for a keyword that indicates DLSS is active because this changes how we navigate the menu
    if kerasService.wait_for_word(word="sharpness", timeout=10, interval=1) is None:
        logging.info("No DLSS Settings Detected")
        # Scroll down graphics menu
        press_n_times("down", 15, 0.2)
    else:
        logging.info("DLSS Settings Detected")
        # Scroll down graphics menu
        press_n_times("down", 17, 0.2)

    if kerasService.wait_for_word(word="volumetric", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the keyword 'volumetric'. Did the the menu scroll correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics_2.png",
        ArtifactType.CONFIG_IMAGE,
        "second picture of graphics settings",
    )

    # Scroll down graphics menu
    press_n_times("down", 15, 0.2)

    if kerasService.wait_for_word(word="hdr", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the keyword 'hdr'. Did the the menu scroll correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics_3.png",
        ArtifactType.CONFIG_IMAGE,
        "third picture of graphics settings",
    )

    # Launch the benchmark
    user.keyDown("tab")
    time.sleep(5)
    user.keyUp("tab")

    setup_end_time = int(time.time())
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logging.info("Setup took %s seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("performance", interval=0.2, timeout=30)
    if not result:
        logging.info("Performance graph was not found! Could not mark the start time.")
        sys.exit(1)

    test_start_time = int(time.time())

    # Wait for benchmark to complete
    time.sleep(112)

    # Wait for results screen to display info
    result = kerasService.wait_for_word("lost", interval=0.1, timeout=11)
    if not result:
        logging.info("Didn't see signal lost. Could not mark the proper end time!")

    test_end_time = round(int(time.time()) - 2)

    result = kerasService.wait_for_word("benchmark", interval=0.5, timeout=15)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    # Give results screen time to fill out, then save screenshot and config file
    time.sleep(2)
    am.take_screenshot(
        "result.png", ArtifactType.RESULTS_IMAGE, "screenshot of benchmark result"
    )
    am.copy_file(LOCAL_USER_SETTINGS, ArtifactType.CONFIG_TEXT, "config file")

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %s seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)
    am.create_manifest()

    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

args = get_args()
kerasService = KerasService(args.keras_host, args.keras_port)

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution(str(LOCAL_USER_SETTINGS))
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
