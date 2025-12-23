"""Rocket League test script"""
import logging
import os
import time
from subprocess import Popen
import sys
import getpass
from pathlib import Path
import vgamepad as vg
from rocket_league_utils import get_resolution, copy_replay, find_epic_executable, get_args

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import LTTGamePadDS4, find_eg_game_version

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
USERNAME = getpass.getuser()
CONFIG_PATH = Path(f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rocket League\\TAGame\\Config\\TASystemSettings.ini")
PROCESS_NAME = "rocketleague.exe"
EXECUTABLE_PATH = find_epic_executable()
GAME_ID = "9773aa1aa54f4f7b80e44bef04986cea%3A530145df28a24424923f5828cc9031a1%3ASugar?action=launch&silent=true"
GAMEFOLDERNAME = "rocketleague"
am = ArtifactManager(LOG_DIRECTORY)
gamepad = LTTGamePadDS4()

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

def camera_cycle(max_attempts=10):
    """Continuously looks for a word using kerasService. If not found in the given time, presses a button.

    :param kerasService: Object that has the method look_for_word().
    :param gamepad: The gamepad object to send button presses.
    :param word: The word to look for.
    :param max_attempts: Maximum times to check before stopping.
    :param check_duration: How long (in seconds) to look for the word before pressing a button.
    :param button: The gamepad button to press if word is not found.
    """
    for _ in range(max_attempts):
        # Try finding the word within check_duration seconds
        found = kerasService.look_for_word(word="player", attempts=2, interval=0.2)

        if found:
            return True  # Stop checking

        # If not found, press the button once
        gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE)

        # Short delay before rechecking
        time.sleep(0.5)

    logging.info("Max attempts reached for checking the camera. Did the game load the save?")
    sys.exit(1)  # Word was not found

def start_game():
    """Start the game"""
    cmd_string = get_run_game_id_command(GAME_ID)
    logging.info("%s %s", EXECUTABLE_PATH, cmd_string)
    return Popen([EXECUTABLE_PATH, cmd_string])


def run_benchmark():
    # pylint: disable-msg=too-many-branches
    """Run the test!"""
    copy_replay()
    setup_start_time = int(time.time())
    start_game()
    time.sleep(30)  # wait for game to load into main menu

    #Looking for Syncing Failed message
    if kerasService.wait_for_word(word="failed", timeout=5, interval=1):
        gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    time.sleep(2)
    #Looking for press start
    if kerasService.wait_for_word(word="press", timeout=30, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    #Looking for news menu close button
    if kerasService.wait_for_word(word="close", timeout=5, interval=1):
        gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE)

    time.sleep(3)

    #Navigating main menu by going to the bottom of the menu first:
    if kerasService.wait_for_word(word="profile", timeout=60, interval=0.5) is None:
        logging.error("Main menu didn't show up. Check settings and try again.")
        sys.exit(1)

    gamepad.single_dpad_press(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST)
    time.sleep(0.5)
    gamepad.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=15, pause=0.8)

    #Navigating to the profile:
    gamepad.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH, n=2, pause=0.8)
    time.sleep(0.5)
    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    time.sleep(1)

    #Entering the match history screen and starting the replay:
    if kerasService.wait_for_word(word="history", timeout=60, interval=0.5) is None:
        logging.error("Didn't navigate to the replays. Check menu options for any anomalies.")
        sys.exit(1)

    gamepad.single_dpad_press(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH)
    time.sleep(0.5)
    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    time.sleep(1)

    if kerasService.look_for_word(word="recent", attempts=10, interval=1):
        logging.info("In Match History menu, navigating to Saved Replays.")
        gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)
        time.sleep(1)

    if kerasService.wait_for_word(word="watch", timeout=60, interval=0.5) is None:
        logging.error("Didn't navigate to the saved replays correctly. Check menu options for any anomalies.")
        sys.exit(1)

    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    #Beginning the "benchmark":
    if kerasService.wait_for_word(word="special", timeout=60, interval=0.5) is None:
        logging.error("Game didn't load map. Check settings and try again.")
        sys.exit(1)

    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    time.sleep(0.8)
    gamepad.single_dpad_press(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST)
    time.sleep(0.8)
    camera_cycle()
    time.sleep(0.5)
    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    logging.info("Benchmark started. Waiting for completion.")
    time.sleep(4)
    test_start_time = int(time.time())

    # wait for benchmark to complete
    time.sleep(359)

    if kerasService.wait_for_word(word="turbopolsa", timeout=10, interval=1) is None:
        logging.info("Couldn't turbopolsa on the field. Did the benchmark play all the way through?")
        sys.exit(1)
    test_end_time = int(time.time())
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS)

    if kerasService.wait_for_word(word="paused", timeout=10, interval=1) is None:
        logging.info("Couldn't find the settings option. Did the pause menu open?")
        sys.exit(1)

    time.sleep(0.5)
    gamepad.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH, n=5, pause=0.8)
    time.sleep(0.5)
    gamepad.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=3, pause=0.8)
    time.sleep(0.5)
    gamepad.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    time.sleep(0.4)

    if kerasService.look_for_word(word="audio", attempts=10, interval=1) is None:
        logging.info("Couldn't find the audio tab. Did the settings menu open?")
        sys.exit(1)

    time.sleep(1)
    logging.info("Navigating to the Video tab.")
    gamepad.button_press_n_times(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT, n=4, pause=0.8)
    time.sleep(1)

    if kerasService.look_for_word(word="window", attempts=10, interval=1) is None:
        logging.info("Couldn't find the window settings header. Did Keras see the right menu?")
        sys.exit(1)

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
        "end_time": seconds_to_milliseconds(end_time),
        "game_version": find_eg_game_version(GAMEFOLDERNAME)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
