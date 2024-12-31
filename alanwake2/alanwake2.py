"""alan wake 2 test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
from subprocess import Popen
from alanwake2_utils import find_epic_executable, copy_save, CONFIG_PATH, get_resolution
import pydirectinput as user
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position

from harness_utils.output import (
    setup_log_directory, write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import press_n_times

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY.joinpath("run")
PROCESS_NAME = "alanwake2.exe"
EXECUTABLE_PATH = find_epic_executable()
GAME_ID = "c4763f236d08423eb47b4c3008779c84%3A93f2a8c3547846eda966cb3c152a026e%3Adc9d2e595d0e4650b35d659f90d41059?action=launch&silent=true"


def setup_logging():
    """default logging config"""
    setup_log_directory(LOG_DIRECTORY)
    logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def get_run_game_id_command(game_id: int) -> str:
    """Build string to launch game"""
    return "com.epicgames.launcher://apps/" + str(game_id)


def start_game():
    """Start the game"""
    cmd_string = get_run_game_id_command(GAME_ID)
    logging.info("%s %s", EXECUTABLE_PATH, cmd_string)
    return Popen([EXECUTABLE_PATH, cmd_string])


def run_benchmark():
    """Run the test!"""

    copy_save()
    setup_start_time = time.time()
    start_game()
    time.sleep(10)  # wait for game to load into main menu

    if kerasService.wait_for_word(word="saving", timeout=30, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    user.press("enter")

    if kerasService.wait_for_word(word="warning", timeout=30, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    user.press("enter")

    if kerasService.wait_for_word(word="continue", timeout=30, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    user.press("enter")

    if kerasService.wait_for_word(word="house", timeout=10, interval=0.5):
        user.press("esc")

    #Navigating main menu:
    is_load_present = kerasService.look_for_word("load", interval=1, attempts=5)
    if is_load_present is None:
        raise ValueError("Load game option does not exist. Did the save get copied correctly?")

    logging.info("Navigating to options to get some screenshots")
    press_n_times("down", 2, 0.2)
    user.press("enter")
    time.sleep(0.2)
    if kerasService.wait_for_word(word="graphics", timeout=60, interval=0.5) is None:
        logging.error("Graphics options not available. Did it navigate to the options correctly?")
        sys.exit(1)
    press_n_times("e", 2, 0.2)
    if kerasService.wait_for_word(word="quality", timeout=60, interval=0.5) is None:
        logging.error("Did not see quality preset. Did it navigate to graphics correctly?")
        sys.exit(1)
    am.take_screenshot("graphics1.png", ArtifactType.CONFIG_IMAGE, "first screenshot of graphics settings")
    time.sleep(0.2)
    press_n_times("down", 18, 0.2)
    if kerasService.wait_for_word(word="terrain", timeout=60, interval=0.5) is None:
        logging.error("Did not see Terrain Quality. Did it navigate to graphics correctly?")
        sys.exit(1)
    am.take_screenshot("graphics2.png", ArtifactType.CONFIG_IMAGE, "second screenshot of graphics settings")
    press_n_times("down", 10, 0.2)
    if kerasService.wait_for_word(word="transparency", timeout=60, interval=0.5) is None:
        logging.error("Did not see Transparency. Did it navigate to graphics correctly?")
        sys.exit(1)
    am.take_screenshot("graphics3.png", ArtifactType.CONFIG_IMAGE, "third screenshot of graphics settings")
    time.sleep(0.2)
    user.press("esc")
    time.sleep(0.2)

    logging.info("Seen the main menu. Loading benchmark.")
    press_n_times("up", 3, 0.2)
    user.press("enter")
    time.sleep(2)

    #Loading the save
    if kerasService.wait_for_word(word="heart", timeout=60, interval=0.5) is None:
        logging.error("Heart not showing in loadable games. Did the save get copied correctly?")
        sys.exit(1)

    press_n_times("right", 3, 0.2)
    user.press("enter")
    time.sleep(0.2)
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    #Starting the benchmark:
    if kerasService.wait_for_word(word="recap", timeout=60, interval=0.5) is None:
        logging.error("Didn't see the word recap. Did the save game load?")
        sys.exit(1)

    test_start_time = time.time()

    # wait for benchmark to complete
    time.sleep(170)

    if kerasService.wait_for_word(word="insane", timeout=60, interval=0.5) is None:
        logging.error("Didn't see the word insane. Did the game crash?")
        sys.exit(1)
    test_end_time = time.time()
    time.sleep(2)
    logging.info("Run completed. Closing game.")
    am.copy_file(CONFIG_PATH, ArtifactType.CONFIG_TEXT, "renderer.ini")
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


try:
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    setup_logging()
    kerasService = KerasService(args.keras_host, args.keras_port)
    am = ArtifactManager(LOG_DIRECTORY)
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    report = {
        "resolution": f"{width}x{height}",
        "start_time": round((start_time * 1000)),
        "end_time": round((end_time * 1000))
    }

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
