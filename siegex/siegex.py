"""Rainbow Six Siege X test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
import subprocess
import vgamepad as vg
import pydirectinput as user
from siegex_utils import read_current_resolution, get_r6s_config_path, find_latest_result_file

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.process import terminate_processes
from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import LTTGamePadDS4

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "rainbowsix.exe"
UPLAY_GAME_ID = 635
GAMEPAD = LTTGamePadDS4()
AM = ArtifactManager(LOG_DIRECTORY)

user.FAILSAFE = False

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

# def start_game():
#     """Launch the game with console enabled and FPS unlocked"""
#     return exec_uplay_run_command(UPLAY_GAME_ID)

def start_game():
    logging.info(f"uplay://launch/{UPLAY_GAME_ID}/0")
    subprocess.run(f'start uplay://launch/{UPLAY_GAME_ID}/0', shell=True)

def run_benchmark():
    """Starts the benchmark"""
    
    start_game()
    setup_start_time = int(time.time())
    time.sleep(60)

    result = kerasService.wait_for_word(word="warning", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the warning upon launch. Did the game launch?")
        sys.exit(1)

    time.sleep(20)

    #Checking for the main menu
    result = kerasService.look_for_word(word="shop", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the main menu. Did the game load?")
        sys.exit(1)

    #Navigating to the options
    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS)

    result = kerasService.wait_for_word(word="options", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the options menu. Was something else on the screen?")
        sys.exit(1)

    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    #Navigating to the display settings and screenshotting
    result = kerasService.wait_for_word(word="general", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the general options. Did it navigate to the settings correctly?")
        sys.exit(1)
    
    GAMEPAD.button_press_n_times(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT, n=3, pause=0.3)

    result = kerasService.wait_for_word(word="monitor", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the monitor. Did it navigate to the display settings correctly?")
        sys.exit(1)

    time.sleep(1)
    AM.take_screenshot("display.png", ArtifactType.CONFIG_IMAGE, "Screenshot of the display settings")
    time.sleep(1)

    #Navigating to the graphics settings and screenshotting
    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)

    result = kerasService.wait_for_word(word="filtering", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the texture filtering setting. Did it navigate to the graphics settings correctly?")
        sys.exit(1)

    time.sleep(1)
    AM.take_screenshot("graphics1.png", ArtifactType.CONFIG_IMAGE, "1st screenshot of the graphics settings")
    time.sleep(1)

    GAMEPAD.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=20, pause=0.3)

    result = kerasService.wait_for_word(word="sharpness", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the TAA sharpness setting. Did it navigate the graphics settings correctly?")
        sys.exit(1)

    time.sleep(1)
    AM.take_screenshot("graphics2.png", ArtifactType.CONFIG_IMAGE, "2nd screenshot of the graphics settings")
    time.sleep(1)

    #Starting the benchmark
    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT)

    elapsed_setup_time = int(time.time() - setup_start_time)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    
    result = kerasService.wait_for_word(word="skip", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the skip dialog. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())
    time.sleep(76)

    result = kerasService.wait_for_word(word="results", interval=0.2, timeout=250)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = int(time.time() - 1)
    time.sleep(1)
    AM.take_screenshot("results.png", ArtifactType.CONFIG_IMAGE, "Screenshot of the results")
    AM.copy_file(find_latest_result_file(), ArtifactType.RESULTS_TEXT, "Benchmark results HTML")

    # Wait 5 seconds for benchmark info
    time.sleep(2)

    # End the run
    elapsed_test_time = int(test_end_time - test_start_time)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    AM.copy_file(get_r6s_config_path(), ArtifactType.CONFIG_TEXT, "GameSettings.ini")
    terminate_processes(PROCESS_NAME)
    logging.info("Waiting for Siege X to fully exit now.")
    time.sleep(30) #sleeping to let the game processes finish closing
    return test_start_time, test_end_time




try:
    start_time, endtime = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": resolution,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
