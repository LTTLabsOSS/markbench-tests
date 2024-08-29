"""Stellaris test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
import pyautogui as gui
import pydirectinput as user

from citiesskylines2_utils import read_current_resolution, copy_launcherfiles, copy_launcherpath, copy_benchmarksave, copy_continuegame

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
from harness_utils.steam import exec_steam_game
from harness_utils.keras_service import KerasService

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

    # Exit
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


def main():
    """main entry point to the script"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    keras_service = KerasService(args.keras_host, args.keras_port, LOG_DIR.joinpath("screenshot.jpg"))

    test_start_time, test_end_time = run_benchmark(keras_service)
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time)
    }

    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
