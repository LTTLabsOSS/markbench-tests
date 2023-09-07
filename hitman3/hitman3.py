import os
import logging
import time
from subprocess import Popen
import pyautogui as gui
import sys

from hitman_3_utils import get_resolution, wait_for_image

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.logging import *
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as STEAM_PATH

STEAM_GAME_ID = 1659040
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_EXECUTABLE = "steam.exe"
PROCESS_NAMES = ['HITMAN3.exe', 'Launcher.exe']


def start_game():
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info(STEAM_PATH + " " + steam_run_arg)
    return Popen([STEAM_PATH, steam_run_arg])


def run_benchmark():
    t1 = time.time()
    start_game()

    options_image = os.path.dirname(os.path.realpath(__file__)) + "/images/hitman3_options.png"
    options_loc = wait_for_image(options_image, 0.7, 1, 15)
    print(f"Options button is here {options_loc}")
    click_me = gui.center(options_loc)
    print(f"Center of options button is here {click_me}")
    gui.click(click_me.x, click_me.y)

    time.sleep(2)
    gui.scroll(-1000)
    time.sleep(2)

    start_image = os.path.dirname(os.path.realpath(__file__)) + "/images/start_benchmark.png"
    start_loc = wait_for_image(start_image, 0.7, 1, 10)
    print(f"Start button is here {start_loc}")
    click_me = gui.center(start_loc)
    print(f"Center of start button is here {click_me}")
    gui.click(click_me.x, click_me.y)

    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
    start_time = time.time()
  
    hitman_title = os.path.dirname(os.path.realpath(__file__)) + "/images/hitman_header.png"
    time.sleep(150) # sleep during benchmark 140 + 10 seconds loading.
    result = wait_for_image(hitman_title, 0.7, 2, 60)
    if not result:
        logging.error("Benchmark failed to complete! Could not find end image")
        exit(1)
    
    end_time = time.time()

    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")
    terminate_processes(*PROCESS_NAMES)
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
    height, width = get_resolution()
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
    terminate_processes(*PROCESS_NAMES)
    exit(1)