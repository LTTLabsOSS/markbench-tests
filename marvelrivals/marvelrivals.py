"""Marvel Rivals test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import pyautogui as gui
import pydirectinput as user
import sys
from marvelrivals_utils import read_resolution
import subprocess

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import mouse_scroll_n_times
from harness_utils.steam import get_app_install_location, get_build_id


SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
STEAM_GAME_ID = 2767030
PROCESS_NAME = "Marvel-Win64-Shipping.exe"
LAUNCHER_NAME = "MarvelRivals_Launcher.exe"
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\Marvel\\Saved\\Config\\Windows"
CONFIG_FILENAME = "GameUserSettings.ini"
cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"

am = ArtifactManager(LOG_DIR)

def setup_logging():
    """default logging config"""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(filename=f'{LOG_DIR}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def start_game():
    """Starts the game process"""
    game_path = get_app_install_location(STEAM_GAME_ID)
    process_path = os.path.join(game_path, LAUNCHER_NAME)  # Full path to the executable
    logging.info(f"Starting game: {process_path}")
    process = subprocess.Popen([process_path], cwd=game_path)
    return process

def run_benchmark(keras_service):
    """Run Marvel Rivals benchmark"""
    setup_start_time = time.time()
    start_game()
    

    #wait for launcher to launch then click the launch button to launch the launcher into the game that we were launching
    time.sleep(20)
    location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\launch_button.png", confidence=0.7) #luckily this seems to be a set resolution for the button
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    time.sleep(60)  # wait for game to load into main menu

    #launching into the game menu
    result = keras_service.wait_for_word("start", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the title screen. Did the game load?")
        sys.exit(1)

    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.5)

    #navigating to the video settings and taking screenshots
    result = keras_service.wait_for_word("play", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the play menu. Did it click the mouse to start the game?")
        sys.exit(1)
    user.press("escape")
    time.sleep(0.5)

    result = keras_service.wait_for_word("settings", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the settings menu. Did it open the menu with escape?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(1)

    result = keras_service.wait_for_word("brightness", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the brightness option. Did the game load into the display options?")
        sys.exit(1)

    am.take_screenshot("video1.png", ArtifactType.CONFIG_IMAGE, "1st picture of video settings")
    time.sleep(1)
    mouse_scroll_n_times(10, -800,  0.2)
    time.sleep(0.5)

    result = keras_service.wait_for_word("foliage", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the foliage option. Did it scroll down far enough?")
        sys.exit(1)

    am.take_screenshot("video2.png", ArtifactType.CONFIG_IMAGE, "2nd picture of video settings")
    time.sleep(1)

    #navigate to the player profile
    user.press("escape")
    time.sleep(1)
    result = keras_service.wait_for_word("play", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the play menu. Did it press escape?")
        sys.exit(1)

    time.sleep(1)
    height, width = read_resolution()
    location = None

    # We check the resolution so we know which screenshot to use for the locate on screen function
    match width:
        case "1280":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\profile_720.png", confidence=0.9)
        case "1920":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\profile_1080.png", confidence=0.9)
        case "2560":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\profile_1440.png", confidence=0.9)
        case "3840":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\profile_2160.png", confidence=0.9)
        case _:
            logging.error("Could not find the profile icon. The game resolution is currently %s, %s. Are you using a standard resolution?", height, width)
            sys.exit(1)
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.5)

    #navigate to the replays section
    result = keras_service.wait_for_word("favorites", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the favorites menu. Did it navigate properly to it?")
        sys.exit(1)
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(1)

    result = keras_service.wait_for_word("match", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the match replays menu. Did it click correctly?")
        sys.exit(1)
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(1)
    
    #starting the benchmark replay
    result = keras_service.wait_for_word("shibuya", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the replay we were looking for. Is it not saved in the favorites?")
        sys.exit(1)
    match width:
        case "1280":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\play_720.png", confidence=0.9)
        case "1920":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\play_1080.png", confidence=0.9)
        case "2560":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\play_1440.png", confidence=0.9)
        case "3840":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\play_2160.png", confidence=0.9)
        case _:
            logging.error("Could not find the play button. The game resolution is currently %s, %s. Are you using a standard resolution?", height, width)
            sys.exit(1)
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.5)

    #marking the in-time
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    time.sleep(2)
    
    #looking for the player name to start wait timer till we get into the actual game
    result = keras_service.wait_for_word("dluo", timeout=30, interval=1)
    if not result:
        logging.info("Did not find the player Dluo. Did the replay start?")
        sys.exit(1)
    time.sleep(90)

    #looking for landmark to mark benchmark start time and then wait for first round to finish
    if keras_service.wait_for_word(word="defend", timeout=30, interval=1) is None:
        logging.info("Didn't see the defend waypoint. Did the game crash?")
        sys.exit(1)
    test_start_time = time.time() + 2
    time.sleep(460)

    #checking that first round has finished
    result = keras_service.wait_for_word("complete", timeout=30, interval=1)
    if not result:
        logging.info("First round doesn't appear to have finished. Did the replay start?")
        sys.exit(1)
    test_end_time = time.time()
    
    am.copy_file(Path(cfg), ArtifactType.CONFIG_TEXT, "Marvel Rivals Video Config")
    logging.info("Run completed. Closing game.")
    time.sleep(2)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(PROCESS_NAME)
    am.create_manifest()
    time.sleep(10)

    return test_start_time, test_end_time


def main():
    """entry point to test script"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()

    keras_service = KerasService(args.keras_host, args.keras_port)

    start_time, end_time = run_benchmark(keras_service)

    height, width = read_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "game_version": get_build_id(STEAM_GAME_ID)
    }

    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("something went wrong running the benchmark!")
        logging.exception(ex)
        sys.exit(1)