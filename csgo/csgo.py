import logging
import os
import time
from argparse import ArgumentParser
from subprocess import Popen
import pyautogui as gui
import pydirectinput as user
import sys


sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import *
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_run_command, get_registry_active_user
from harness_utils.keras_service import KerasService
from utils import get_resolution, copy_benchmark

"""
Fortunately with Counter Strike we have access to the developer console which lets us
execute things via keyboard input right from the load menu.
"""
STEAM_USER_ID = get_registry_active_user()
STEAM_GAME_ID = 730
MAP = "de_dust2"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "csgo.exe"


def is_word_on_screen(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result != None:
            return True
        time.sleep(delay_seconds)
    return False


def console_command(command):
    for char in command:
        gui.press(char)
    user.press("enter")

def main_menu() -> any:
    return is_word_on_screen(word="news", attempts=50, delay_seconds=3)

def in_game() -> any:
    return is_word_on_screen(word="terrorists", attempts=50, delay_seconds=1)

def finished() -> any:
    return is_word_on_screen(word="finished", attempts=25, delay_seconds=1)


def run_benchmark():
    logging.info(f"User ID is: {STEAM_USER_ID}")
    copy_benchmark()
    t1 = time.time()
    exec_steam_run_command(STEAM_GAME_ID)
    time.sleep(30)  # wait for game to load into main menu

    start_game_screen= time.time()
    while (True):
        if main_menu():
            logging.info('Game started. Loading map.')
            user.press("`")
            time.sleep(1)
            console_command(f"map {MAP}")
            time.sleep(5)  # wait for map to load
            break
        elif time.time()-start_game_screen>60:
            logging.info("Game didn't start in time. Check settings and try again.")
            exit(1)
        logging.info("Game hasn't started. Trying again in 5 seconds")
        time.sleep(5)


    #Running the benchmark:
    loading_screen= time.time()
    while (True):
        if in_game():
            logging.info('Map loaded. Starting benchmark.')
            time.sleep(1)
            user.press("`")
            time.sleep(0.5)
            console_command("exec benchmark")
            time.sleep(0.5)
            console_command("benchmark")
            t2 = time.time()
            logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
            start_time = time.time()
            time.sleep(43) #approximate wait time
            break
        elif time.time()-loading_screen>60:
            logging.info("Game didn't load map. Check settings and try again.")
            exit(1)
        logging.info("Game hasn't finished loading map. Trying again in 5 seconds")
        time.sleep(5)

    # wait for benchmark to complete
    
    benchmark= time.time()
    while (True):
        if finished():
            logging.info('Benchmark finished. Finishing benchmark')
            break
        elif time.time()-benchmark>60:
            logging.info("Game didn't finish. Check settings and try again.")
            exit(1)
        logging.info("Game hasn't finished running. Trying again in 5 seconds")
        time.sleep(5)
      
    end_time = time.time()
    logging.info(f"Benchmark took {round((end_time - start_time), 2)} seconds")
    terminate_processes(PROCESS_NAME)
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
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(
    LOG_DIRECTORY, "screenshot.jpg")) 


try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    result = {
        "resolution": f"{width}x{height}",
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
