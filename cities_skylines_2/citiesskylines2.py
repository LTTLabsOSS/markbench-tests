"""Stellaris test script"""
from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import pyautogui as gui
import pydirectinput as user

from citiesskylines2_utils import read_current_resolution, copy_launcherfiles, copy_launcherpath, copy_benchmarksave, copy_continuegame

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.process import terminate_processes
from harness_utils.output import (
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.steam import exec_steam_game, get_build_id
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import mouse_scroll_n_times


SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "cities2.exe"
STEAM_GAME_ID = 949230
launcher_files = [
    "bootstrapper-v2.exe",
    "launcher.exe",
    "notlauncher-options.json"
]
save_files = [
    "Benchmark.cok",
    "Benchmark.cok.cid"
]
config_files = [
    "continue_game.json",
    "UserState.coc"
]

APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = Path(f"{APPDATA}\\..\\LocalLow\\Colossal Order\\Cities Skylines II")
CONFIG_FILENAME = "launcher-settings.json"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"

user.FAILSAFE = False

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
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(STEAM_GAME_ID)


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")


def run_benchmark(keras_service):
    """Starts the benchmark"""
    copy_launcherfiles(launcher_files)
    copy_launcherpath()
    copy_benchmarksave(save_files)
    copy_continuegame(config_files)

    am = ArtifactManager(LOG_DIR)

    start_game()
    setup_start_time = time.time()
    time.sleep(14)

    result = keras_service.wait_for_word("paradox", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the paused notification. Unable to mark start time!")
        sys.exit(1)
    user.press("esc")
    user.press("esc")
    user.press("esc")
    time.sleep(20)

    result = keras_service.wait_for_word("grand", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the paused notification. Unable to mark start time!")
        sys.exit(1)
    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    time.sleep(2)
    logging.info('Starting benchmark')
    user.press("3")
    time.sleep(2)

    # TODO: switch back to 180 after testing
    test_start_time = time.time()
    time.sleep(180)

    test_end_time = time.time()
    time.sleep(2)
    user.press("1")

    # Wait 5 seconds for benchmark info
    time.sleep(10)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Open quick menu
    user.press("esc")
    time.sleep(0.2)

    result = keras_service.look_for_word("options", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the options menu. Did the game open the quick dialog menu properly?")
        sys.exit(1)

    # Navigate to options menu
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.click()
    time.sleep(0.2)

    am.take_screenshot("general.png", ArtifactType.CONFIG_IMAGE, "general settings menu")

    result = keras_service.look_for_word("graphics", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the graphics menu. Did the game navigate to the general settings correctly?")
        sys.exit(1)

    # Navigate to graphics menu
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.click()
    time.sleep(0.2)

    am.take_screenshot("graphics_1.png", ArtifactType.CONFIG_IMAGE, "first picture of graphics settings menu")

    result = keras_service.look_for_word("window", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the keyword 'window' in graphics menu. Did the game navigate to the graphics menu correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)

    mouse_scroll_n_times(8, -800,  0.2)

    if keras_service.wait_for_word(word="water", timeout=30, interval=1) is None:
        logging.info("Did not find the keyword 'water' in menu. Did the game scroll correctly?")
        sys.exit(1)
    am.take_screenshot("graphics_2.png", ArtifactType.CONFIG_IMAGE, "second picture of graphics settings menu")

    mouse_scroll_n_times(8, -400,  0.2)

   # verify that we scrolled through the menu correctly
    if keras_service.wait_for_word(word="texture", timeout=30, interval=1) is None:
        logging.info("Did not find the keyword 'texture' in menu. Did the game scroll correctly?")
        sys.exit(1)
    am.take_screenshot("graphics_3.png", ArtifactType.CONFIG_IMAGE, "third picture of graphics settings menu")
    am.copy_file(CONFIG_FULL_PATH, ArtifactType.CONFIG_TEXT, "config file")

    # Exit
    terminate_processes(PROCESS_NAME)
    am.create_manifest()

    return test_start_time, test_end_time


def main():
    """main entry point to the script"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    keras_service = KerasService(args.keras_host, args.keras_port)

    test_start_time, test_end_time = run_benchmark(keras_service)
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID)
    }

    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
