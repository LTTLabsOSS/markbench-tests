"""Total War: Warhammer III test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import pyautogui as gui
import pydirectinput as user
from twwh3_utils import read_current_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.steam import get_app_install_location
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "Warhammer3.exe"
STEAM_GAME_ID = 1142710

APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Warhammer3\\scripts"
CONFIG_FILENAME = "preferences.script.txt"

cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"

user.FAILSAFE = False


def start_game():
    """Starts the game process"""
    cmd_string = f"start /D \"{get_app_install_location(STEAM_GAME_ID)}\" {PROCESS_NAME}"
    logging.info(cmd_string)
    return os.system(cmd_string)


def skip_logo_screens() -> None:
    """Simulate input to skip logo screens"""
    logging.info("Skipping logo screens")

    # Enter menu
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)


def run_benchmark():
    """Starts the benchmark"""
    start_game()
    setup_start_time = time.time()
    time.sleep(5)
    
    am = ArtifactManager(LOG_DIRECTORY)

    result = kerasService.look_for_word("warning", attempts=10, interval=5)
    if not result:
        logging.info("Did not see warnings. Did the game start?")
        sys.exit(1)

    skip_logo_screens()
    time.sleep(2)

    result = kerasService.look_for_word("options", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the options menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    am.take_screenshot("main.png", ArtifactType.CONFIG_IMAGE, "picture of basic settings")

    result = kerasService.look_for_word("ad", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the advanced menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.5)

    am.take_screenshot("advanced.png", ArtifactType.CONFIG_IMAGE, "picture of advanced settings")

    result = kerasService.look_for_word("bench", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the benchmark menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    if args.benchmark != "battle":
        result = kerasService.look_for_word("mirrors", attempts=10, interval=1)
        gui.moveTo(result["x"], result["y"])
        time.sleep(0.2)
        gui.mouseDown()
        time.sleep(0.2)
        time.sleep(2)
        user.press("enter")
    else:
        time.sleep(2)
        user.press("enter")

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("fps", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = time.time()

    if args.benchmark != "battle":
        time.sleep(65) # Wait time for MOM benchmark
    else:
        time.sleep(100)  # Wait time for battle benchmark

    result = kerasService.wait_for_word("summary", interval=0.2, timeout=250)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = time.time() - 1

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    am.take_screenshot("result.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    am.copy_file(Path(cfg), ArtifactType.RESULTS_TEXT, "preferences.script.txt")

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
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
parser.add_argument("-s", "--benchmark", dest="benchmark",
                    help="Benchmark Scene", metavar="benchmark", required=True)
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(
    LOG_DIRECTORY, "screenshot.jpg"))

try:
    start_time, endtime = run_benchmark()
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
