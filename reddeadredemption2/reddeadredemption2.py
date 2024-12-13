"""Red Dead Redemption 2 test script"""
import logging
import os
import time
import sys
import pydirectinput as user

from red_dead_redemption_2_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_run_command

STEAM_GAME_ID = 1174180
PROCESS_NAME = "RDR2"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")


def run_benchmark():
    """Starts the benchmark"""
    # Wait for game to load to main menu
    setup_start_time = time.time()
    exec_steam_run_command(STEAM_GAME_ID)
    time.sleep(80)

    # Press Z to enter settings
    user.press("z")
    time.sleep(3)

    # Enter graphics menu
    ## ensure we are starting from the top left of the screen
    user.press("up")
    user.press("up")
    user.press("left")
    user.press("left")

    user.press("down")
    user.press("enter")
    time.sleep(3)

    # Run benchmark by holding X for 2 seconds
    user.keyDown('x')
    time.sleep(1.5)
    user.keyUp("x")

    # Press enter to confirm benchmark
    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    user.press("enter")
    test_start_time = time.time()

    # Wait for the benchmark to complete
    time.sleep(315)  # 5 min, 15 seconds.
    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

try:
    start_time, end_time = run_benchmark()
    width, height = get_resolution()
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
