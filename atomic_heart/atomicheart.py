"""Atomic Heart test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
import pydirectinput as user
from utils import read_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.steam import exec_steam_run_command, get_app_install_location, get_build_id
from harness_utils.misc import remove_files, press_n_times
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.ocr_service import OcrService
from harness_utils.artifacts import ArtifactManager, ArtifactType

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\AtomicHeart\\Saved\\Config\\WindowsNoEditor"
CONFIG_FILENAME = "GameUserSettings.ini"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
PROCESS_NAME = "AtomicHeart"
STEAM_GAME_ID = 668580
VIDEO_PATH = os.path.join(
    get_app_install_location(STEAM_GAME_ID), "AtomicHeart", "Content", "Movies")

intro_videos = [
    os.path.join(VIDEO_PATH, "Launch_4k_60FPS_PS5.mp4"),
    os.path.join(VIDEO_PATH, "Launch_4k_60FPS_XboxXS.mp4"),
    os.path.join(VIDEO_PATH, "Launch_FHD_30FPS_PS4.mp4"),
    os.path.join(VIDEO_PATH, "Launch_FHD_30FPS_XboxOne.mp4"),
    os.path.join(VIDEO_PATH, "Launch_FHD_60FPS_PC_Steam.mp4")
]

user.FAILSAFE = False

def navigate_game_menus(am: ArtifactManager):
    """Navigate in game menus and take screenshots where appropriate"""
    result = kerasService.wait_for_word("vsync", timeout=25)
    if not result:
        logging.info("Did not see display menu. Did we navigate to the options correctly?")
        sys.exit(1)
    am.take_screenshot("display.png", ArtifactType.CONFIG_IMAGE, "screenshot of the display settings")

    user.press("e")
    time.sleep(0.5)
    result = kerasService.wait_for_word("dlss", timeout=25)
    if not result:
        logging.info("Did not see the top of quality menu. Did we navigate to the quality menu correctly?")
        sys.exit(1)
    am.take_screenshot("quality_1.png", ArtifactType.CONFIG_IMAGE, "first screenshot of quality menu")

    user.press("w")
    time.sleep(0.5)
    result = kerasService.wait_for_word("vegetation", timeout=25)
    if not result:
        logging.info("Did not see the bottom of quality menu. Did we scroll the quality menu correctly?")
        sys.exit(1)
    am.take_screenshot("quality_2.png", ArtifactType.CONFIG_IMAGE, "second screenshot of quality menu")
    user.press("esc")
    time.sleep(0.5)

def run_benchmark():
    """Starts the benchmark"""
    remove_files(intro_videos)
    exec_steam_run_command(STEAM_GAME_ID)
    am = ArtifactManager(LOG_DIRECTORY)
    setup_start_time = int(time.time())

    time.sleep(10)

    result = kerasService.wait_for_word("press", timeout=25)
    if not result:
        logging.info("Did not see start screen")
        sys.exit(1)

    user.press("space")

    # This is for the menu checking for if there's a continue option
    result = kerasService.look_for_word("continue", attempts=20, interval=1)
    if result:
        logging.info("Continue option available, navigating accordingly.")
        press_n_times("s", 3, 0.5)
        user.press("f")
        time.sleep(0.5)
        navigate_game_menus(am)

        # Launch benchmark
        user.press("s")
        time.sleep(0.5)
        user.press("d")
        time.sleep(0.5)
        user.press("f")
        time.sleep(0.5)
        user.press("space")
    else:
        logging.info("Continue option not available, navigating accordingly.")
        user.press("s")
        time.sleep(0.5)
        user.press("f")
        time.sleep(0.5)
        navigate_game_menus(am)

        # Launch benchmark
        user.press("s")
        time.sleep(0.5)
        user.press("w")
        time.sleep(0.5)
        user.press("d")
        time.sleep(0.5)
        user.press("f")
        time.sleep(0.5)
        user.press("space")

    time.sleep(10)

    # This is for the loading screen continue
    result = kerasService.wait_for_word("continue", interval=1, timeout=80)
    if not result:
        logging.info("Did not see the option to continue. Check settings and try again.")
        sys.exit(1)

    logging.info("Continue found. Starting opening scene benchmark.")
    user.press("space")

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("vibes", interval=0.5, timeout=250)
    if not result:
        logging.info("Good vibes were not found! Could not mark the start time.")
        sys.exit(1)

    test_start_time = int(time.time())

    time.sleep(216) # Wait for benchmark till the end time

    result = kerasService.wait_for_word("83", interval=0.5, timeout=250)
    if not result:
        logging.info("Waypoint distance was not found! Could not mark the end time.")
        sys.exit(1)

    test_end_time = int(time.time())

    time.sleep(13) # wait for No Rest For the Wicked Quest

    result = kerasService.wait_for_word("wicked", interval=1, timeout=250)
    if not result:
        logging.info("Wicked was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    logging.info("Wicked found. Ending Benchmark.")
    am.copy_file(CONFIG_FULL_PATH, ArtifactType.CONFIG_TEXT, "GameUserSettings.ini")

    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    am.create_manifest()

    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

parser = ArgumentParser()
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = OcrService(args.keras_host, args.keras_port)

try:
    start_time, end_time = run_benchmark()
    height, width = read_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
