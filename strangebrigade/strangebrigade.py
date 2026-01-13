"""Strange Brigade test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import pyautogui as gui
import pydirectinput as user
from strangebrigade_utils import read_current_resolution, replace_exe, restore_exe

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.misc import remove_files, press_n_times
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.steam import get_app_install_location, exec_steam_run_command, get_build_id
from harness_utils.ocr_service import OcrService, ScreenSplitConfig, ScreenShotDivideMethod, ScreenShotQuadrant
from harness_utils.artifacts import ArtifactManager, ArtifactType

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "StrangeBrigade.exe"
STEAM_GAME_ID = 312670
capture_path = os.path.join(SCRIPT_DIRECTORY, "capture")
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{LOCALAPPDATA}\\Strange Brigade"
CONFIG_FILENAME = "GraphicsOptions.ini"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
EXE_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "bin")
VIDEO_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "FMV")

top_right_quad = ScreenSplitConfig(
    divide_method=ScreenShotDivideMethod.QUADRANT,  # Choose appropriate split method
    quadrant=ScreenShotQuadrant.TOP_RIGHT  # Choose the correct quadrant
)

user.FAILSAFE = False

intro_videos = [
    os.path.join(VIDEO_PATH, "rebellion.webm")
]

def run_benchmark():
    """Starts the benchmark"""
    logging.info(intro_videos)
    remove_files(intro_videos)
    replace_exe()
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    time.sleep(30)
    am = ArtifactManager(LOG_DIRECTORY)

    result = kerasService.look_for_word_vulkan("options", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the options menu. Did the game launch?")
        sys.exit(1)

    press_n_times("down", 5, 0.2)
    user.press("left")
    time.sleep(0.2)
    user.press("enter")

    result = kerasService.look_for_word_vulkan("display", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the display menu. Did keras navigate correctly?")
        sys.exit(1)

    gui.press("pgdn")

    result = kerasService.look_for_word_vulkan("customise", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the customize graphics detail option. Did navigate correctly?")
        sys.exit(1)

    am.take_screenshot_vulkan("display.png", ArtifactType.CONFIG_IMAGE, "picture of display settings")

    time.sleep(0.5)
    user.press("escape")

    press_n_times("down", 5, 0.2)
    user.press("enter")

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word_vulkan("strange", interval=0.5, timeout=100, split_config=top_right_quad)
    if not result:
        logging.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())

    time.sleep(55)  # Wait time for battle benchmark

    result = kerasService.wait_for_word_vulkan("confirm", interval=0.2, timeout=250)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = int(time.time()) - 1

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    am.take_screenshot_vulkan("result.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    am.copy_file(Path(CONFIG_FULL_PATH), ArtifactType.RESULTS_TEXT, "preferences.script.txt")

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    am.create_manifest()
    time.sleep(5)
    restore_exe()

    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.INFO)
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
    start_time, endtime = run_benchmark()
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
