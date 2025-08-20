"""Doom: The Dark Ages test script"""
import logging
from argparse import ArgumentParser
from pathlib import Path
import os.path
import time
import sys
import pydirectinput as user
import re
from doomdarkages_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from doomdarkages_utils import copy_launcher_config
from harness_utils.steam import exec_steam_game, get_build_id
from harness_utils.keras_service import KerasService
from harness_utils.misc import press_n_times, mouse_scroll_n_times
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.artifacts import ArtifactManager, ArtifactType



SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "DOOMTheDarkAges"
STEAM_GAME_ID = 3017860
username = os.getlogin()
BENCHMARK_RESULTS_PATH = f"C:\\Users\\{username}\\Saved Games\\id Software\\DOOMTheDarkAges\\base\\benchmark"

def start_game():
    """Launch the game with no launcher or start screen"""
    copy_launcher_config()
    return exec_steam_game(STEAM_GAME_ID, game_params=["+com_skipIntroVideo", "1"])

def find_latest_result_file(base_path):
    """Look for files in the benchmark results path that match the pattern in the regular expression"""
    base_path = Path(base_path)

    try:
        return max(
            base_path.glob("benchmark-*.json"),
            key=lambda p: p.stat().st_mtime
        )
    except ValueError:
        raise FileNotFoundError(
            f"No benchmark-*.json files found in {base_path}"
        )

def run_benchmark():
    """Runs the actual benchmark."""
    start_game()
    am = ArtifactManager(LOG_DIRECTORY)

    setup_start_time = int(time.time())
    time.sleep(25)
    # Press space to proceed to the main menu
    result = kerasService.wait_for_word_vulkan("press", timeout=80)
    if not result:
        logging.info("Didn't see title screen. Check settings and try again.")
        sys.exit(1)

    logging.info("Hit the title screen. Continuing")
    time.sleep(2)
    user.press("space")
    time.sleep(4)

    # Navigate menus and take screenshots using the artifact manager
    result = kerasService.wait_for_word_vulkan("campaign", interval=3, timeout=60)
    if not result:
        logging.info("Didn't land on the main menu!")
        sys.exit(1)

    logging.info("Saw the main menu. Proceeding.")
    time.sleep(1)

    press_n_times("down", 3, 0.2)
    user.press("enter")
    time.sleep(1)

    result = kerasService.wait_for_word_vulkan("daze", interval=3, timeout=15)
    if not result:
        logging.info("Didn't see the game settings. Did it navigate correctly?")
        sys.exit(1)

    logging.info("Saw the game settings. Proceeding.")
    press_n_times("q", 2, 0.2)
    time.sleep(1)

    # Screenshotting the display settings
    result = kerasService.wait_for_word_vulkan("display", interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the video settings. Did it navigate correctly?")
        sys.exit(1)

    am.take_screenshot_vulkan("video1.png", ArtifactType.CONFIG_IMAGE, "1st screenshot of video settings menu")
    mouse_scroll_n_times(6, -200,  0.2)
    time.sleep(1)

    result = kerasService.wait_for_word_vulkan("nvidia", interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the NVIDIA Reflex setting. Did it navigate correctly?")
        sys.exit(1)

    am.take_screenshot_vulkan("video2.png", ArtifactType.CONFIG_IMAGE, "2nd screenshot of video settings menu")
    mouse_scroll_n_times(6, -200,  0.2)
    time.sleep(1)

    result = kerasService.wait_for_word_vulkan("advanced", interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the advanced heading. Did it navigate correctly?")
        sys.exit(1)

    am.take_screenshot_vulkan("video3.png", ArtifactType.CONFIG_IMAGE, "3rd screenshot of video settings menu")
    mouse_scroll_n_times(5, -200,  0.2)
    time.sleep(1)

    result = kerasService.wait_for_word_vulkan("shading", interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the shading quality setting. Did it navigate correctly?")
        sys.exit(1)

    am.take_screenshot_vulkan("video4.png", ArtifactType.CONFIG_IMAGE, "4th screenshot of video settings menu")
    mouse_scroll_n_times(5, -220,  0.2)
    time.sleep(0.2)

    result = kerasService.wait_for_word_vulkan("brightness", interval=3, timeout=15)
    if not result:
        logging.info("Didn't find the brightness setting. Did it navigate correctly?")
        sys.exit(1)

    am.take_screenshot_vulkan("video5.png", ArtifactType.CONFIG_IMAGE, "5th screenshot of video settings menu")
    user.press("escape")
    time.sleep(0.2)

    # Navigating to the benchmark
    result = kerasService.wait_for_word_vulkan("campaign", interval=3, timeout=20)
    if not result:
        logging.info("Didn't land on the main menu!")
        sys.exit(1)

    logging.info("Saw the main menu. Proceeding.")
    time.sleep(1)

    user.press("up")
    user.press("enter")
    time.sleep(1)

    result = kerasService.wait_for_word_vulkan("benchmarks", interval=3, timeout=15)
    if not result:
        logging.info("Didn't navigate to the extras menu. Did it navigate properly?")
        sys.exit(1)

    logging.info("Saw the extras menu. Proceeding.")
    time.sleep(1)

    user.press("up")
    user.press("enter")
    time.sleep(1)

    result = kerasService.wait_for_word_vulkan("abyssal", interval=3, timeout=15)
    if not result:
        logging.info("Don't see the Abyssal Forest benchmark option. Did it navigate properly?")
        sys.exit(1)

    logging.info("See the benchmarks. Starting the Abyssal Forest benchmark level.")
    time.sleep(1)

    press_n_times("down", 2, 0.2)
    user.press("enter")
    time.sleep(1)

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word_vulkan("frame", interval=0.5, timeout=90)
    if not result:
        logging.info("Benchmark didn't start. Did the game crash?")
        sys.exit(1)

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    test_start_time = int(time.time()) + 8

    # Sleeping for the duration of the benchmark
    time.sleep(110)

    test_end_time = None

    result = kerasService.wait_for_word_vulkan("results", interval=0.5, timeout=90)
    if result:
        logging.info("Found the results screen. Marking the out time.")
        test_end_time = int(time.time()) - 2
        time.sleep(2)
    else:
        logging.info("Results screen was not found!" +
            "Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    logging.info("Results screen was found! Finishing benchmark.")
    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)
    am.take_screenshot_vulkan("result.png", ArtifactType.RESULTS_IMAGE, "screenshot of results")
    am.copy_file(results_file, ArtifactType.RESULTS_TEXT, "benchmark results/settings xml file")

    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)
    am.create_manifest()

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

parser = ArgumentParser()
parser.add_argument(
    "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True
)
parser.add_argument(
    "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True
)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port)

try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
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
