import logging
import os
import pydirectinput as user
import time
from subprocess import Popen
import sys

from red_dead_redemption_2_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.logging import *
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as STEAM_PATH

STEAM_GAME_ID = 1174180
PROCESS_NAME = "RDR2"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")

config_path = os.path.join(os.environ["HOMEPATH"], "Documents" ,"Rockstar Games", "Red Dead Redemption 2", "Settings", "system.xml")


def start_game():
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info(STEAM_PATH + " " + steam_run_arg)
    return Popen([STEAM_PATH, steam_run_arg])


def run_benchmark():
    ##
    # Wait for game to load to main menu
    ##
    t1 = time.time()
    start_game()
    time.sleep(65)

    ##
    # Press Z to enter settings
    ##
    user.press("z")
    time.sleep(3)

    ##
    # Enter graphics menu
    ##
    ## ensure we are starting from the top left of the screen
    user.press("up")
    user.press("up")
    user.press("left")
    user.press("left")

    user.press("down")
    user.press("enter")
    time.sleep(3)

    ##
    # Run benchmark by holding X for 2 seconds
    ##
    user.keyDown('x')
    time.sleep(1.5)
    user.keyUp("x")

    ##
    # Press enter to confirm benchmark
    ##
    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
    user.press("enter")
    start_time = time.time()

    ##
    # Wait for the benchmark to complete
    ##
    time.sleep(315)  # 5 min, 15 seconds.
    end_time = time.time()
    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")

    # Exit
    terminate_processes(PROCESS_NAME)
    return start_time, end_time


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
    width, height = get_resolution(config_path)
    result = {
        "resolution": format_resolution(width, height),
        "graphics_preset": "current",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    exit(1)
