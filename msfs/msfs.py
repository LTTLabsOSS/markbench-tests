"""Microsoft Flight Simulator test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
from pathlib import Path
import pyautogui as gui
import pydirectinput as user
from msfs_utils import read_current_resolution, copy_flight, install_mod

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
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import press_n_times, mouse_scroll_n_times

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "FlightSimulator.exe"
STEAM_GAME_ID = 1250410
flight_files = [
    "benchmark2.FLT",
    "benchmark2.PLN",
    "benchmark2.SPB"
]
APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = Path(f"{APPDATA}\\Microsoft Flight Simulator")
CONFIG_FILENAME = "UserCfg.opt"
cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
am = ArtifactManager(LOG_DIRECTORY)

user.FAILSAFE = False

def start_game():
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-FastLaunch"])

def type_thing(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")

def run_benchmark():
    """Starts the benchmark"""
    copy_flight(flight_files)
    install_mod()
    start_game()
    setup_start_time = time.time()
    time.sleep(15)

    result = kerasService.look_for_word("warning", attempts=10, interval=1)
    if result:
        result = kerasService.look_for_word("normal", attempts=10, interval=1)
        gui.moveTo(result["x"], result["y"])
        gui.move(10,0)
        time.sleep(0.2)
        gui.mouseDown()
        time.sleep(0.2)
        gui.mouseUp()
        time.sleep(0.2)
        press_n_times("enter", 4, 0.2)
        time.sleep(15)
        result = kerasService.look_for_word("plan", attempts=10, interval=1)
        if not result:
            logging.info("Did not find the world map menu. Did the game launch?")
            sys.exit(1)

        press_n_times("right", 4, 0.2)
        user.press("up")
        time.sleep(0.2)
        user.press("enter")
    else:
        result = kerasService.wait_for_word("plan", interval=0.2, timeout=250)
        if not result:
            logging.info("Did not find the world map menu. Did the game launch?")
            sys.exit(1)

        gui.moveTo(result["x"], result["y"])
        gui.move(0,10)
        time.sleep(0.2)
        gui.mouseDown()
        time.sleep(0.2)
        gui.mouseUp()
        time.sleep(0.2)
        press_n_times("enter", 2, 0.2)
        time.sleep(1)

    result = kerasService.look_for_word("more", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the more options. Did keras click correctly?")
        sys.exit(1)

    press_n_times("space", 2, 0.5)
    time.sleep(2)

    result = kerasService.look_for_word("load", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the save loading menu. Please check settings and try again.")
        sys.exit(1)

    press_n_times("down", 2, 0.5)
    user.press("enter")
    time.sleep(1)
    type_thing("benchmark2.flt")
    time.sleep(1)

    result = kerasService.look_for_word("fly", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the fly button. Did it open the load screen correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(3)

    #grabbing screenshots of settings
    result = kerasService.look_for_word("ready", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the fly button. Did the game load?")
        sys.exit(1)

    user.press("esc")
    time.sleep(0.5)

    
    result = kerasService.look_for_word("general", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the general settings. Did the game load?")
        sys.exit(1)

    
    press_n_times("down", 5, 0.3)
    user.press("left")
    time.sleep(0.2)
    user.press("up")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(1)

    result = kerasService.look_for_word("resolution", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the resolution settings. Did it open the graphics settings?")
        sys.exit(1)

    am.take_screenshot("graphics1.png", ArtifactType.CONFIG_IMAGE, "first picture of graphics settings")

    user.press("left")
    time.sleep(0.2)
    user.press("right")
    time.sleep(0.2)
    press_n_times("down", 24, 0.3)

    result = kerasService.look_for_word("waves", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the water waves setting. Did it scroll correctly?")
        sys.exit(1)

    am.take_screenshot("graphics2.png", ArtifactType.CONFIG_IMAGE, "second picture of graphics settings")

    press_n_times("down", 13, 0.3)

    result = kerasService.look_for_word("flare", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the lens flare setting. Did it scroll correctly?")
        sys.exit(1)

    am.take_screenshot("graphics3.png", ArtifactType.CONFIG_IMAGE, "third picture of graphics settings")

    user.press("down")

    am.take_screenshot("graphics4.png", ArtifactType.CONFIG_IMAGE, "last picture of graphics settings")

    result = kerasService.look_for_word("traffic", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the traffic settings. Did keras click correctly?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    gui.move(0,10)
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)
    press_n_times("enter", 2, 0.2)

    result = kerasService.look_for_word("ferries", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the ships and ferries setting. Did it open the traffic settings?")
        sys.exit(1)

    am.take_screenshot("traffic1.png", ArtifactType.CONFIG_IMAGE, "first picture of traffic settings")

    user.press("up")
    time.sleep(0.2)
    user.press("down")
    time.sleep(0.2)
    user.press("right")
    time.sleep(0.2)
    press_n_times("down", 8, 0.3)

    result = kerasService.look_for_word("variety", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the traffic variety setting. Did it scroll correctly?")
        sys.exit(1)

    am.take_screenshot("traffic2.png", ArtifactType.CONFIG_IMAGE, "second picture of traffic settings")

    press_n_times("esc", 2, 0.3)

    #starting the benchmark
    result = kerasService.wait_for_word("ready", interval=0.2, timeout=250)
    if not result:
        logging.info("Did not find the ready to fly button. Did the game load?")
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(2)

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("parking", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the parking brake objective. Unable to mark start time!")
        sys.exit(1)

    test_start_time = time.time()
    user.keyDown("ctrlleft")
    user.keyDown("altleft")
    user.press("x")
    user.keyUp("altleft")
    user.keyUp("ctrlleft")
    time.sleep(650)

    result = kerasService.wait_for_word("taxi", interval=0.2, timeout=100)
    if not result:
        logging.info(
            "Taxi objective was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = time.time()

    am.copy_file(Path(cfg), ArtifactType.CONFIG_TEXT, "msfs video config")

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    # End the run
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

parser = ArgumentParser()
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port)

try:
    start_time, endtime = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": resolution,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime)
    }
    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
