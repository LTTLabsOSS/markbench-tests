"""Rocket League test script"""
import logging
import os
import time
from subprocess import Popen
import pyautogui as gui
import pydirectinput as user
import sys
import getpass
from pathlib import Path
from rocket_league_utils import get_resolution, copy_replay, find_rocketleague_executable, get_args

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.misc import press_n_times
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
USERNAME = getpass.getuser()
CONFIG_PATH = Path(f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rocket League\\TAGame\\Config\\TASystemSettings.ini")
PROCESS_NAME = "rocketleague.exe"
EXECUTABLE_PATH = find_rocketleague_executable()
GAME_ID = "9773aa1aa54f4f7b80e44bef04986cea%3A530145df28a24424923f5828cc9031a1%3ASugar?action=launch&silent=true"
am = ArtifactManager(LOG_DIRECTORY)

setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

args = get_args()
kerasService = KerasService(args.keras_host, args.keras_port)


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
    copy_replay()
    setup_start_time = time.time()
    start_game()
    time.sleep(30)  # wait for game to load into main menu

    if kerasService.wait_for_word(word="press", timeout=30, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    user.press("enter")

    is_close_present = kerasService.look_for_word("close", interval=1, attempts=5)
    if is_close_present:
        gui.moveTo(is_close_present[0], is_close_present[1])
        time.sleep(0.2)
        gui.mouseDown()
        time.sleep(0.2)
        gui.mouseUp()
        time.sleep(1)

    time.sleep(3)

    # Navigating main menu:
    if kerasService.wait_for_word(word="profile", timeout=60, interval=0.5) is None:
        logging.error("Main menu didn't show up. Check settings and try again.")
        sys.exit(1)

    user.press("left")
    time.sleep(0.2)
    user.press("up")
    time.sleep(0.2)
    user.press("up")
    time.sleep(0.2)
    user.press("up")
    time.sleep(0.2)
    user.press("up")
    time.sleep(0.2)

    if kerasService.look_for_word(word="esports", attempts=5, interval=0.2):
        logging.info('Saw esports. Navigating accordingly.')
        user.press("down")
        time.sleep(0.2)

    if kerasService.look_for_word(word="shop", attempts=10, interval=0.2):
        logging.info('Saw item shop. Navigating accordingly.')
        user.press("down")
        time.sleep(0.2)

    if kerasService.look_for_word(word="pass", attempts=5, interval=0.2):
        logging.info('Saw rocket pass. Navigating accordingly.')
        user.press("down")
        time.sleep(0.2)

    user.press("down")
    time.sleep(0.2)
    user.press("down")
    time.sleep(0.2)

    user.press("enter")
    time.sleep(1)

    #Entering the match history screen and starting the replay:
    if kerasService.wait_for_word(word="history", timeout=60, interval=0.5) is None:
        logging.error("Didn't navigate to the replays. Check menu options for any anomalies.")
        sys.exit(1)

    #Entering the replay screen and starting the replay:
    user.press("down")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(1)

    result = kerasService.look_for_word("saved", attempts=10, interval=1)
    if not result:
        logging.info("Couldn't find the saved replays tab. Check settings and try again.")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)
    user.press("enter")

    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    #Beginning the "benchmark":
    if kerasService.wait_for_word(word="special", timeout=60, interval=0.5) is None:
        logging.error("Game didn't load map. Check settings and try again.")
        sys.exit(1)

    user.press("shiftleft")
    time.sleep(0.2)
    user.press("left")
    time.sleep(0.2)
    gui.click(button='right')
    time.sleep(0.2)
    gui.click(button='right')
    time.sleep(0.2)
    gui.click(button='right')
    time.sleep(0.2)
    gui.click(button='right')
    time.sleep(0.2)
    gui.click(button='right')
    time.sleep(0.2)
    user.press("shiftleft")
    logging.info("Benchmark started. Waiting for completion.")
    time.sleep(4)
    test_start_time = time.time()

    # wait for benchmark to complete
    time.sleep(359)

    test_end_time = time.time()
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    user.press("esc")
    time.sleep(0.4)
    press_n_times("down", 3, 0.5)
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.4)

    result = kerasService.look_for_word("video", attempts=10, interval=1)
    if not result:
        logging.info("Couldn't find the video tab. Did the settings menu open?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(1)
    result = kerasService.look_for_word("basic", attempts=10, interval=1)
    if not result:
        logging.info("Couldn't find the basic settings header. Did Keras click correctly?")
        sys.exit(1)
    else:
        logging.info("Seen the video settings, capturing the data.")
    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "Screenshot of the display settings")

    am.copy_file(CONFIG_PATH, ArtifactType.CONFIG_TEXT, "TASystemSettings.ini")

    logging.info("Run completed. Closing game.")
    time.sleep(2)
    terminate_processes(PROCESS_NAME)
    am.create_manifest()
    return test_start_time, test_end_time


try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
