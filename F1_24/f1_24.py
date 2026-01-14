"""F1 24 test script"""
import logging
from argparse import ArgumentParser
import os.path
import re
import time
import sys
import pydirectinput as user
from f1_24_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.steam import exec_steam_run_command, get_app_install_location, get_build_id
from harness_utils.ocr_service import OCRService
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
from harness_utils.artifacts import ArtifactManager, ArtifactType

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "F1_24"
STEAM_GAME_ID = 2488620
VIDEO_PATH = os.path.join(get_app_install_location(STEAM_GAME_ID), "videos")

username = os.getlogin()
CONFIG_PATH = f"C:\\Users\\{username}\\Documents\\My Games\\F1 24\\hardwaresettings"
CONFIG_FILENAME = "hardware_settings_config.xml"
CONFIG = f"{CONFIG_PATH}\\{CONFIG_FILENAME}"
BENCHMARK_RESULTS_PATH = f"C:\\Users\\{username}\\Documents\\My Games\\F1 24\\benchmark"

intro_videos = [
    os.path.join(VIDEO_PATH, "attract.bk2"),
    os.path.join(VIDEO_PATH, "cm_f1_sting.bk2")
]
user.FAILSAFE = False


def find_latest_result_file(base_path):
    """Look for files in the benchmark results path that match the pattern in the regular expression"""
    pattern = r"benchmark_.*\.xml"
    list_of_files = []

    for filename in os.listdir(base_path):
        if re.search(pattern, filename, re.IGNORECASE):
            list_of_files.append(base_path + '\\' +filename)

    latest_file = max(list_of_files, key=os.path.getmtime)

    return latest_file

def find_settings() -> any:
    """Look for and enter settings"""
    if not kerasService.look_for_word("settings", attempts=5, interval=3):
        logging.info("Didn't find settings!")
        sys.exit(1)
    user.press("enter")
    time.sleep(1.5)


def find_graphics() -> any:
    """Look for and enter graphics settings"""
    if not kerasService.look_for_word("graphics", attempts=5, interval=3):
        logging.info("Didn't find graphics!")
        sys.exit(1)
    user.press("right")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(1.5)


def navigate_startup():
    """press space through the warnings and navigate startup menus"""
    result = kerasService.wait_for_word("product", timeout=80)
    if not result:
        logging.info("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    user.press("space")
    time.sleep(1)
    user.press("space")
    time.sleep(1)
    user.press("space")
    time.sleep(4)

    # Press enter to proceed to the main menu
    result = kerasService.wait_for_word("press", interval=2, timeout=80)
    if not result:
        logging.info("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    logging.info("Hit the title screen. Continuing")
    user.press("enter")
    time.sleep(1)

    # cancel logging into ea services
    result = kerasService.wait_for_word("login", timeout=50)
    if result:
        logging.info("Cancelling logging in.")
        user.press("enter")
        time.sleep(2)

def offline_menu():
    """Navigateout of the offline menu"""
    result = kerasService.wait_for_word("signed", timeout=50)
    if not result:
        logging.info("Didn't find the keyword 'signed'")
        return
    user.press("enter")
def run_benchmark():
    """Runs the actual benchmark."""
    remove_files(intro_videos)
    exec_steam_run_command(STEAM_GAME_ID)
    am = ArtifactManager(LOG_DIRECTORY)

    setup_start_time = int(time.time())
    time.sleep(2)
    navigate_startup()

    offline_menu()

    # Navigate menus and take screenshots using the artifact manager
    result = kerasService.wait_for_word("theatre", interval=3, timeout=60)
    if not result:
        logging.info("Didn't land on the main menu!")
        sys.exit(1)

    logging.info("Saw the options! we are good to go!")
    time.sleep(1)

    press_n_times("down", 6, 0.2)
    user.press("enter")
    time.sleep(2)
    #find_settings()
    find_graphics()

    # Navigate to video settings
    press_n_times("down", 3, 0.2)
    user.press("enter")
    time.sleep(0.2)

    result = kerasService.wait_for_word("vsync", interval=3, timeout=60)
    if not result:
        logging.info("Didn't find the keyword 'vsync'. Did the program navigate to the video mode menu correctly?")
        sys.exit(1)
    press_n_times("down", 18, 0.2)

    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "screenshot of video settings menu")
    user.press("esc")
    time.sleep(0.2)

    result = kerasService.wait_for_word("steering", interval=3, timeout=60)
    if not result:
        logging.info("Didn't find the keyword 'steering'. Did the program exit the video mode menu correctly?")
        sys.exit(1)

    # Navigate through graphics settings and take screenshots of all settings contained within
    am.take_screenshot("graphics_1.png", ArtifactType.CONFIG_IMAGE, "first screenshot of graphics settings")
    press_n_times("down", 29, 0.2)

    result = kerasService.wait_for_word("chromatic", interval=3, timeout=60)
    if not result:
        logging.info("Didn't find the keyword 'chromatic'. Did we navigate the menu correctly?")
        sys.exit(1)

    am.take_screenshot("graphics_2.png", ArtifactType.CONFIG_IMAGE, "second screenshot of graphics settings")
    press_n_times("up", 28, 0.2)
    user.press("enter")
    time.sleep(0.2)

    # Navigate benchmark menu
    if not kerasService.look_for_word("weather", attempts=5, interval=3):
        logging.info("Didn't find weather!")
        sys.exit(1)

    am.take_screenshot("benchmark.png", ArtifactType.CONFIG_IMAGE, "screenshot of benchmark settings")

    press_n_times("down", 6, 0.2)
    user.press("enter")
    time.sleep(2)

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("lap", interval=0.5, timeout=90)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    test_start_time = int(time.time()) + 8

    # sleep for 3 laps
    time.sleep(310)

    test_end_time = None

    result = kerasService.wait_for_word("loading", interval=0.5, timeout=90)
    if result:
        logging.info("Found the loading screen. Marking the out time.")
        test_end_time = int(time.time()) - 2
        time.sleep(2)
    else:
        logging.info("Could not find the loading screen. Could not mark end time!")

    result = kerasService.wait_for_word("results", interval=3, timeout=90)
    if not result:
        logging.info("Results screen was not found!" +
            "Did harness not wait long enough? Or test was too long?")
        sys.exit(1)
    logging.info("Results screen was found! Finishing benchmark.")
    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)
    am.take_screenshot("result.png", ArtifactType.RESULTS_IMAGE, "screenshot of results")
    am.copy_file(CONFIG, ArtifactType.CONFIG_TEXT, "config file")
    am.copy_file(results_file, ArtifactType.RESULTS_TEXT, "benchmark results xml file")

    if test_end_time is None:
        logging.info("Loading screen end time not found. Using results screen fallback time.")
        test_end_time = int(time.time())

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
kerasService = OCRService(args.keras_host, args.keras_port)

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
