"""Red Dead Redemption 2 test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
import pydirectinput as user
from pathlib import Path
import getpass

from red_dead_redemption_2_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.misc import press_n_times
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.steam import exec_steam_run_command, get_build_id
from harness_utils.artifacts import ArtifactManager, ArtifactType

STEAM_GAME_ID = 1174180
PROCESS_NAME = "RDR2"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
CONFIG_FULL_PATH = Path("C:/Users/", getpass.getuser(), "Documents", "Rockstar Games", "Red Dead Redemption 2", "Settings", "system.xml")


def run_benchmark():
    """Starts the benchmark"""
    # Wait for game to load to main menu
    setup_start_time = time.time()
    exec_steam_run_command(STEAM_GAME_ID)
    am = ArtifactManager(LOG_DIRECTORY)
    time.sleep(80)

    # Press Z to enter settings
    result = kerasService.look_for_word_vulkan("settings", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the settings menu. Did the game launch?")
        sys.exit(1)
    user.press("z")
    time.sleep(3)

    # Enter graphics menu
    ## ensure we are starting from the top left of the screen
    result = kerasService.look_for_word_vulkan("graphics", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the graphics menu. Did keras get stuck?")
        sys.exit(1)
    user.press("up")
    user.press("up")
    user.press("left")
    user.press("left")
    user.press("down")
    user.press("enter")
    time.sleep(3)

    # Take pictures of the graphics settings
    result = kerasService.look_for_word_vulkan("resolution", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the resolution setting. Did the game navigate correctly?")
        sys.exit(1)
    am.take_screenshot("Graphics1.png", ArtifactType.RESULTS_IMAGE, "1st Graphics Screenshot")
    press_n_times("down", 26, 0.2)

    result = kerasService.look_for_word_vulkan("msaa", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the MSAA settings. Did Keras navigate correctly?")
        sys.exit(1)
    am.take_screenshot("Graphics2.png", ArtifactType.RESULTS_IMAGE, "2nd Graphics Screenshot")
    press_n_times("down", 14, 0.2)

    result = kerasService.look_for_word_vulkan("reflection", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the Water Reflection Quality settings. Did Keras navigate correctly?")
        sys.exit(1)
    am.take_screenshot("Graphics3.png", ArtifactType.RESULTS_IMAGE, "3rd Graphics Screenshot")
    press_n_times("down", 12, 0.2)

    result = kerasService.look_for_word_vulkan("tessellation", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the Tree Tessellation settings. Did Keras navigate correctly?")
        sys.exit(1)
    am.take_screenshot("Graphics4.png", ArtifactType.RESULTS_IMAGE, "4th Graphics Screenshot")

    # Run benchmark by holding X for 2 seconds
    result = kerasService.look_for_word_vulkan("benchmark", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the options menu. Did the game launch?")
        sys.exit(1)
    user.keyDown('x')
    time.sleep(1.5)
    user.keyUp("x")

    # Press enter to confirm benchmark
    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    user.press("enter")

    # Looking for the word Stop to mark the in time
    result = kerasService.look_for_word_vulkan("stop", attempts=60, interval=1)
    if not result:
        logging.info("Did not find the stop benchmarking in the corner. Did the benchmark crash?")
        sys.exit(1)
    test_start_time = time.time()

    # Wait for the benchmark to complete
    time.sleep(270)  # 4 min, 30 seconds.
    result = kerasService.look_for_word_vulkan("end", attempts=30, interval=1)
    if not result:
        logging.info("Did not find the end results screen. Did the benchmark crash?")
        sys.exit(1)
    test_end_time = time.time()
    am.take_screenshot("Results.png", ArtifactType.RESULTS_IMAGE, "Results Screenshot")
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    am.copy_file(Path(CONFIG_FULL_PATH), ArtifactType.RESULTS_TEXT, "system.xml")

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
