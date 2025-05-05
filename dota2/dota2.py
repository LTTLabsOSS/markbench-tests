"""Dota 2 test script"""
import logging
from pathlib import Path
import time
import pyautogui as gui
import pydirectinput as user
import sys
from dota2_utils import get_resolution, copy_replay, copy_config, get_args

sys.path.insert(1, str(Path(__file__).resolve().parent.parent))

from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.steam import exec_steam_game
from harness_utils.artifacts import ArtifactManager, ArtifactType


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "dota2.exe"
STEAM_GAME_ID = 570

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


def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(
        STEAM_GAME_ID, game_params=["-console", "+fps_max 0"])


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")


def run_benchmark():
    """Run dota2 benchmark"""
    am = ArtifactManager(LOG_DIRECTORY)
    copy_replay()
    copy_config()
    setup_start_time = int(time.time())
    start_game()
    time.sleep(10)  # wait for game to load into main menu

    # to skip logo screen
    if kerasService.wait_for_word(word="va", timeout=20, interval=1):
        logging.info('Game started. Entering main menu')
        user.press("esc")
        time.sleep(1)

    # waiting about a minute for the main menu to appear
    if kerasService.wait_for_word(
            word="heroes", timeout=80, interval=1) is None:
        logging.error(
            "Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    height, width = get_resolution()
    location = None
    click_multiple = 0
    # We check the resolution so we know which screenshot to use for the locate on screen function
    match width:
        case "1280":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_720.png",
                confidence=0.9)
            click_multiple = 0.8
        case "1920":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1080.png")
            click_multiple = 1
        case "2560":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1440.png")
            click_multiple = 1.5
        case "3840":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_2160.png")
            click_multiple = 2
        case _:
            logging.error(
                "Could not find the settings cog. The game resolution is currently %s, %s. Are you using a standard resolution?",
                height, width)
            sys.exit(1)

    # navigating to the video config section
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    result = kerasService.look_for_word(word="video", attempts=10, interval=1)
    if not result:
        logging.info(
            "Did not find the video menu button. Did Keras enter settings correctly?")
        sys.exit(1)

    gui.moveTo(result["x"] + int(50 * click_multiple),
               result["y"] + int(20 * click_multiple))
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    if kerasService.wait_for_word(
            word="resolution", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE,
                       "picture of video settings")

    # starting the benchmark
    user.press("escape")
    logging.info('Starting benchmark')
    user.press("\\")
    time.sleep(0.2)
    console_command("exec_async benchmark")
    time.sleep(1)
    user.press("\\")

    time.sleep(5)
    if kerasService.wait_for_word(
            word="directed", timeout=30, interval=0.1) is None:
        logging.error("Didn't see directed camera. Did the replay load?")
        sys.exit(1)

    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    time.sleep(23)

    # Default fallback start time
    test_start_time = int(time.time())

    result = kerasService.wait_for_word(word="2560", timeout=30, interval=0.1)
    if result is None:
        logging.error(
            "Unable to find Leshrac's HP. Using default start time value.")
    else:
        test_start_time = int(time.time())
        logging.info("Found Leshrac's HP! Marking the start time accordingly.")

    time.sleep(73)  # sleep duration during gameplay

    # Default fallback end time
    test_end_time = int(time.time())

    result = kerasService.wait_for_word(word="1195", timeout=30, interval=0.1)
    if result is None:
        logging.error(
            "Unable to find gold count of 1195. Using default end time value.")
    else:
        test_end_time = int(time.time())
        logging.info("Found the gold. Marking end time.")

    time.sleep(2)

    if kerasService.wait_for_word(
            word="heroes", timeout=25, interval=1) is None:
        logging.error("Main menu after running benchmark not found, exiting")
        sys.exit(1)

    time.sleep(4)
    logging.info("Run completed. Closing game.")

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(PROCESS_NAME)
    am.create_manifest()
    return test_start_time, test_end_time


try:
    start_time, end_time = run_benchmark()
    res_height, res_width = get_resolution()
    report = {
        "resolution": format_resolution(res_width, res_height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
