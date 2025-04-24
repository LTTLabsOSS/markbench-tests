from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import time
import sys
import re
import pydirectinput as user

sys.path.insert(1, os.path.join(sys.path[0], '..'))

#pylint: disable=wrong-import-position
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.steam import get_app_install_location, get_build_id, exec_steam_game
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import press_n_times

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "ACShadows.exe" #-----------------------------------------------------------------------
STEAM_GAME_ID = 3159330
CONFIG_LOCATION = f"C:\\Users\\Administrator\\Documents\\Assassin's Creed Shadows" #-----------------------------------------------------------------------
CONFIG_FILENAME = "ACShadows.ini"#-----------------------------------------------------------------------

user.FAILSAFE = False

def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"FullscreenWidth=(\d+)")
    width_pattern = re.compile(r"FullscreenHeight=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)

def find_word(keras_service, word, msg, timeout = 30, interval = 1):
    if keras_service.wait_for_word(word = word, timeout = timeout, interval = interval) is None:
        logging.info(msg)
        sys.exit(1)


def int_time():
    return int(time.time())

#function to delete intro videos
def delete_videos():
    return

def start_game():
    """Starts the game process"""
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")

def run_benchmark(keras_service):
    start_game()
    setup_start_time = int_time()
    am = ArtifactManager(LOG_DIR)
    time.sleep(20)

    if keras_service.wait_for_word(word="animus", timeout=30, interval = 1) is None:
        logging.info("did not find main menu")
        sys.exit(1)

    user.press("f1")

    find_word(keras_service, "system", "couldn't find system")

    user.press("down")

    time.sleep(1)

    user.press("space")

    find_word(keras_service, "benchmark", "couldn't find benchmark")

    #take pictures of settings here
    user.press("space")

    time.sleep(1)

    am.take_screenshot("display1.png", ArtifactType.CONFIG_IMAGE, "display settings 1")

    press_n_times("down", 13, 0.3)

    am.take_screenshot("display2.png", ArtifactType.CONFIG_IMAGE, "display settings 2")

    press_n_times("down", 4, 0.3)

    am.take_screenshot("display3.png", ArtifactType.CONFIG_IMAGE, "display settings 3")

    user.press("c")

    time.sleep(1)

    am.take_screenshot("scalability1.png", ArtifactType.CONFIG_IMAGE, "scalability settings 1")

    press_n_times("down", 10, 0.3)

    am.take_screenshot("scalability2.png", ArtifactType.CONFIG_IMAGE, "scalability settings 2")

    press_n_times("down", 6, 0.3)

    am.take_screenshot("scalability3.png", ArtifactType.CONFIG_IMAGE, "scalability settings 3")

    press_n_times("down", 5, 0.3)

    am.take_screenshot("scalability4.png", ArtifactType.CONFIG_IMAGE, "scalability settings 4")

    user.press("esc")

    #exit settings

    user.press("down")

    time.sleep(1)

    user.press("space")

    setup_end_time = int_time()
    elapsed_setup_time = setup_end_time - setup_start_time

    if keras_service.wait_for_word(word = "benchmark", timeout = 30, interval = 1) is None:
        logging.info("did not find benchmark")
        sys.exit(1)

    test_start_time = int_time()

    time.sleep(100)

    if keras_service.wait_for_word(word = "results", timeout = 30, interval = 1) is None:
        logging.info("did not find end screen")
        sys.exit(1)

    test_end_time = int_time()
    elapsed_test_time = test_end_time - test_start_time
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    am.take_screenshot("benchmark_results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")

    user.press("x")
    
    time.sleep(1)

    user.press("esc")
    time.sleep(10)

    terminate_processes(PROCESS_NAME)
    am.create_manifest()

    return test_start_time, test_end_time

def setup_logging():
    """setup logging"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=f'{LOG_DIR}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def main():
    logging.info("main function")
    """entry point"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    args = parser.parse_args()
    keras_service = KerasService(args.keras_host, args.keras_port)
    start_time, endtime = run_benchmark(keras_service)
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID)
    }
    logging.info("right before write report")
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