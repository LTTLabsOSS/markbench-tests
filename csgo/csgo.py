import logging
import os
import time
from argparse import ArgumentParser
import pyautogui as gui
import pydirectinput as user
import sys

from csgo_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import *
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_run_command, get_steam_folder_path

"""
Fortunately with Counter Strike we have access to the developer console which lets us
execute things via keyboard input right from the load menu.
"""

STEAM_GAME_ID = 730
MAP = "de_dust2"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")


def console_command(command):
    for char in command:
        gui.press(char)
    user.press("enter")


def run_benchmark():
    t1 = time.time()
    exec_steam_run_command(STEAM_GAME_ID)
    time.sleep(40)  # wait for game to load into main menu

    # open developer console in main menu
    user.press("`")

    # load map
    console_command(f"map {MAP}")
    time.sleep(40)  # wait for map to load

    # open developer console in map
    user.press("`")
    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
    console_command("exec benchmark")
    console_command("benchmark")
    start_time = time.time()
    time.sleep(50)  # wait for benchmark to complete
    end_time = time.time()
    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")
    terminate_processes("csgo")
    return start_time, end_time


# Entry Point
setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

parser = ArgumentParser()
args = parser.parse_args() # This probably isn't working because there isn't steamid arg in manifest
config_path = f"{get_steam_folder_path()}\\userdata\\{args.steamid}\\{STEAM_GAME_ID}\\local\\cfg\\video.txt"

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution(config_path)
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
    terminate_processes("csgo")
    exit(1)
