import logging
from subprocess import Popen
import sys

from cv2_utils import *
from utils import read_resolution, try_install_paths, get_local_drives

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.logging import *
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as steam_path 

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
STEAM_GAME_ID = 1286680
EXECUTABLE = "Wonderlands.exe"


def start_game() -> any:
    game_process = None
    try:
        exec_path = try_install_paths(get_local_drives())
        game_process = Popen(exec_path)
    except ValueError:
        logging.info("Could not find executable, trying a steam launch")
        pass

    if game_process is None:
        steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
        logging.info(steam_path + " " + steam_run_arg)
        game_process = Popen([steam_path, steam_run_arg])


def run_benchmark():
    start_game()
    
    t1 = time.time()

    # wait for menu to load
    time.sleep(30)

    wait_and_click("options", "options menu", ClickType.HARD)
    wait_and_click("benchmark", "benchmark menu", ClickType.HARD)
    wait_and_click("start", "start benchmark", ClickType.HARD)
    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")

    start_time = time.time()

    time.sleep(124)
    wait_for_image_on_screen("options", 0.8, 2, 60)

    end_time = time.time()
    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")
    terminate_processes("Wonderlands")
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
    height, width = read_resolution()
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
    terminate_processes("Wonderlands")
    exit(1)
