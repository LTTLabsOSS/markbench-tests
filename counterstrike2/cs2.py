"""Counter-Strike 2 test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import pyautogui as gui
import pydirectinput as user
import sys
from cs2_utils import get_resolution, copy_config

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService
from harness_utils.steam import exec_steam_game, get_registry_active_user, get_steam_folder_path, get_build_id
from harness_utils.artifacts import ArtifactManager, ArtifactType


SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "cs2.exe"
STEAM_GAME_ID = 730

STEAM_USER_ID = get_registry_active_user()
cfg = Path(get_steam_folder_path(), "userdata", str(STEAM_USER_ID), str(STEAM_GAME_ID), "local", "cfg", "cs2_video.txt")

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
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-console", "+fps_max 0"])


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")


def run_benchmark(keras_service):
    """Run cs2 benchmark"""
    copy_config()
    setup_start_time = time.time()
    start_game()
    am = ArtifactManager(LOG_DIR)
    time.sleep(20)  # wait for game to load into main menu

    result = keras_service.wait_for_word("play", timeout=30, interval=0.1)
    if not result:
        logging.info("Did not find the play menu. Did the game load?")
        sys.exit(1)

    height, width = get_resolution()
    location = None

    # We check the resolution so we know which screenshot to use for the locate on screen function
    match width:
        case "1920":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\settings_1080.png")
        case "2560":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\settings_1440.png")
        case "3840":
            location = gui.locateOnScreen(f"{SCRIPT_DIR}\\screenshots\\settings_2160.png")
        case _:
            logging.error("Could not find the settings cog. The game resolution is currently %s, %s. Are you using a standard resolution?", height, width)
            sys.exit(1)

    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    result = keras_service.look_for_word(word="video", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the video menu button. Did Keras enter settings correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    if keras_service.wait_for_word(word="brightness", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "picture of video settings")

    result = keras_service.look_for_word(word="advanced", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the advanced video menu. Did Keras click correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    am.take_screenshot("advanced_video_1.png", ArtifactType.CONFIG_IMAGE, "first picture of advanced video settings")

    result = keras_service.look_for_word(word="boost", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the keyword 'Boost' in the advanced video menu. Did Keras click correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(1)
    gui.scroll(-6000000)
    time.sleep(1)

    if keras_service.wait_for_word(word="particle", timeout=30, interval=1) is None:
        logging.info("Did not find the keyword 'Particle' in advanced video menu. Did Keras scroll correctly?")
        sys.exit(1)
    am.take_screenshot("advanced_video_2.png", ArtifactType.CONFIG_IMAGE, "second picture of advanced video settings")

    logging.info('Starting benchmark')
    user.press("`")
    time.sleep(0.5)
    console_command(r"exec maps\de_dust2_benchmark")
    time.sleep(1)
    console_command("ui_playsettings_maps_workshop @workshop/3240880604/de_dust2_benchmark")
    time.sleep(1)
    console_command("map_workshop 3240880604 de_dust2_benchmark")
    time.sleep(1)
    user.press("`")

    time.sleep(3)
    if keras_service.wait_for_word(word="benchmark", timeout=30, interval=0.1) is None:
        logging.error("Didn't see the title of the benchmark. Did the map load?")
        sys.exit(1)

    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    time.sleep(1)

    # Default fallback start time
    test_start_time = time.time()

    result = keras_service.wait_for_word(word="roll", timeout=30, interval=0.1)
    if result is None:
        logging.error("Didn't see \'lets roll\'. Did the map load?")
    else:
        test_start_time = time.time()
        logging.info("Saw \'lets roll\'! Marking the time.")

    time.sleep(112) # sleep duration during gameplay

    # Default fallback end time
    test_end_time = time.time()

    result = keras_service.wait_for_word(word="console", timeout=30, interval=0.1)
    if result is None:
        logging.error("The console didn't open. Please check settings and try again.")
        sys.exit(1)
    else:
        test_end_time = time.time()
        logging.info("The console opened. Marking end time.")

    # allow time for result screen to populate
    time.sleep(8)

    am.take_screenshot("result.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    am.copy_file(Path(cfg), ArtifactType.CONFIG_TEXT, "cs2 video config")
    logging.info("Run completed. Closing game.")
    time.sleep(2)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_processes(PROCESS_NAME)
    am.create_manifest()

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

    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID)
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
