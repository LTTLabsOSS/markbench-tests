"""Far Cry 6 test script"""
import os
import logging
import time
import pyautogui as gui
import pydirectinput as user
import sys
from argparse import ArgumentParser
import subprocess

from farcry6_utils import get_resolution

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
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import press_n_times, mouse_scroll_n_times

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "FarCry6.exe"
GAME_ID = 5266
username = os.getlogin()
xml_file = rf"C:\Users\{username}\Documents\My Games\Far Cry 6\gamerprofile.xml"


user.FAILSAFE = False

def start_game():
    subprocess.run(f'start uplay://launch/{GAME_ID}/0', shell=True)

def skip_logo_screens() -> None:
    """Simulate input to skip logo screens"""
    logging.info("Skipping logo screens")

    #skipping the logo screens
    press_n_times("escape", 8, 1)

def run_benchmark():
    am = ArtifactManager(LOG_DIRECTORY)
    start_game()
    setup_start_time = int(time.time())
    time.sleep(25)

    #skipping game intros
    result = kerasService.look_for_word("warning", attempts=20, interval=1)
    if not result:
        logging.info("Did not see warnings. Did the game start?")
        sys.exit(1)

    skip_logo_screens()

    result = kerasService.look_for_word("original", attempts=20, interval=1)
    if not result:
        logging.info("Did not see the Far Cry 6 intro video. Did the game crash?")
        sys.exit(1)

    user.press("space")
    user.press("space")

    time.sleep(2)

    #navigating the menus to get to the video settings
    result = kerasService.look_for_word("later", attempts=5, interval=1)
    if result:
        user.press("escape")

    result = kerasService.look_for_word("options", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the main menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    result = kerasService.look_for_word("video", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the options menu. Did keras click incorrectly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    #grabbing screenshots of all the video settings
    result = kerasService.look_for_word("adapter", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the Video Adapter setting in the monitor options. Did keras navigate wrong?")
        sys.exit(1)

    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "picture of video settings")

    time.sleep(2)

    user.press("e")

    result = kerasService.look_for_word("filtering", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the Texture Filtering setting in the quality options. Did keras navigate wrong?")
        sys.exit(1)

    am.take_screenshot("quality1.png", ArtifactType.CONFIG_IMAGE, "1st picture of quality settings")

    time.sleep(2)

    mouse_scroll_n_times(8, -800,  0.2)

    result = kerasService.look_for_word("shading", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the FidelityFX Variable Shading setting in the quality options. Did keras navigate wrong?")
        sys.exit(1)

    am.take_screenshot("quality2.png", ArtifactType.CONFIG_IMAGE, "2nd picture of quality settings")

    time.sleep(2)

    press_n_times("e", 2, 0.2)

    result = kerasService.look_for_word("lock", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the Enable Framerate Lock setting in the advanced options. Did keras navigate wrong?")
        sys.exit(1)

    am.take_screenshot("advanced.png", ArtifactType.CONFIG_IMAGE, "picture of advanced settings")

    #starting the benchmark
    time.sleep(2)
    user.press("f5")
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.look_for_word("toggle", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the toggle ui button in the lower right. Did the benchmark crash?")
        sys.exit(1)
    test_start_time = int(time.time())

    time.sleep(60) # wait for benchmark to complete

    result = kerasService.wait_for_word("results", interval=0.5, timeout=100)
    if not result:
        logging.info("Didn't find the results screen. Did the benchmark crash?")
        sys.exit(1)

    test_end_time = int(time.time()) - 1

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    time.sleep(1)

    # Exit
    terminate_processes(PROCESS_NAME)
    am.copy_file(xml_file, ArtifactType.CONFIG_TEXT, "config file")
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
    test_start_time, test_end_time = run_benchmark()
    width, height = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": "unknown"
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)