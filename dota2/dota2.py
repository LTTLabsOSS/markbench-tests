"""Dota 2 test script"""
import logging
from pathlib import Path
import time
import pyautogui as gui
import pydirectinput as user
import sys
from dota2_utils import get_resolution, verify_replay, copy_replay, copy_config, get_args

sys.path.insert(1, str(Path(sys.path[0]).parent))

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


setup_log_directory(str(LOG_DIRECTORY))
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
am = ArtifactManager(LOG_DIRECTORY)

user.FAILSAFE = False

def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(
        STEAM_GAME_ID, game_params=["-console", "+fps_max 0", "-novid"])


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")

def harness_setup():
    verify_replay()
    copy_replay()
    copy_config()

def screenshot_settings():
    screen_height, screen_width = get_resolution()
    location = None
    click_multiple = 0
    # We check the resolution so we know which screenshot to use for the locate on screen function
    match screen_width:
        case "1280":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_720.png",
                confidence=0.9)
            click_multiple = 0.8
        case "1920":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1080.png",
                confidence=0.9)
            click_multiple = 1
        case "2560":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1440.png",
                confidence=0.9)
            click_multiple = 1.5
        case "3840":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_2160.png",
                confidence=0.9)
            click_multiple = 2
        case _:
            logging.error(
                "Could not find the settings cog. The game resolution is currently %s, %s. Are you using a standard resolution?",
                screen_height, screen_width)
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

    am.take_screenshot("video1.png", ArtifactType.CONFIG_IMAGE,
                       "picture of video settings")

    user.press("down")

    if kerasService.wait_for_word(
            word="api", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    am.take_screenshot("video2.png", ArtifactType.CONFIG_IMAGE,
                       "picture of video settings")

    user.press("down")

    if kerasService.wait_for_word(
            word="direct", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    am.take_screenshot("video3.png", ArtifactType.CONFIG_IMAGE,
                       "picture of video settings")
    
def load_the_benchmark():
    user.press("escape")
    logging.info('Starting benchmark')
    user.press("\\")
    time.sleep(0.5)
    console_command("sv_cheats true")
    time.sleep(1)
    console_command("exec_async benchmark_load")
    time.sleep(5)
    if kerasService.wait_for_word(
            word="directed", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the directed camera. Did the replay load?")
        sys.exit(1)
    console_command("sv_cheats true")
    time.sleep(1)
    console_command("exec_async benchmark_run")
    user.press("\\")

def run_benchmark():
    """Run dota2 benchmark"""
    harness_setup()
    setup_start_time = int(time.time())
    start_game()
    time.sleep(10)  # wait for game to load into main menu

    # waiting about a minute for the main menu to appear
    if kerasService.wait_for_word(
            word="heroes", timeout=80, interval=1) is None:
        logging.error(
            "Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    time.sleep(15)  # wait for main menu
    screenshot_settings()
    
    # starting the benchmark
    load_the_benchmark()

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
        "resolution": format_resolution(int(res_width), int(res_height)),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(str(LOG_DIRECTORY), "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
