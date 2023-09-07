import json
from subprocess import Popen

import psutil

from cv2_utils import *

INSTALL_DIR = "D:\XboxGames\Microsoft Flight Simulator\Content"
EXECUTABLE = "FlightSimulator.exe"
START = 'cmd.exe /C start shell:AppsFolder\Microsoft.FlightSimulator_8wekyb3d8bbwe!App "-FastLaunch"'


def start_game():
    # https://www.pcgamingwiki.com/wiki/Microsoft_Flight_Simulator_(2020)
    # start_cmd = INSTALL_DIR + "\\" + EXECUTABLE
    logging.info(START)
    return Popen(START.split(" "))


def run_benchmark():
    game_process = start_game()
    t1 = time.time()

    # click past safe mode warning modal if exist
    # try:
    move_mouse_to('normal_mode', DEFAULT_TIMEOUT)
    wait_and_click('normal_mode', "warning modal", ClickType.HARD)
    # except:
    #     pass

    # wait for game to load
    time.sleep(90)

    # Navigate to the landing challenges
    wait_and_click('activities', "activities", ClickType.HARD, threshold=0.8)
    wait_and_click('landing_challenges', "landing challenges", ClickType.HARD, threshold=0.90)
    wait_and_click('famous', "famous challenges", ClickType.HARD)
    wait_and_click('jackson', "jackson", ClickType.HARD, threshold=0.77)
    wait_for_image_on_screen('fly', DEFAULT_TIMEOUT)
    t2 = time.time()

    # Press ctrl enter to fly
    user.keyDown('ctrl')
    user.keyDown('enter')
    user.keyUp('ctrl')
    user.keyUp('enter')

    # Wait for map to load
    wait_for_image_on_screen('kjac_loaded', 30)
    logging.info(f"Setup took {round((t2 - t1), 2)} seconds")
    global START_TIME
    START_TIME = time.time()

    # Fly for 80 seconds
    time.sleep(80)

    global END_TIME
    END_TIME = time.time()
    logging.info(f"Benchark took {round((END_TIME - START_TIME), 2)} seconds")

    for proc in psutil.process_iter():
        if "FlightSimulator" in proc.name():
            proc.terminate()


script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)

logging_format = '%(asctime)s %(levelname)-s %(message)s'
logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=logging_format,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(logging_format)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

try:
    run_benchmark()
    result = {
        "resolution": "unknown",
        "graphics_preset": "current",
        "start_time": round((START_TIME * 1000)), # seconds * 1000 = millis
        "end_time": round((END_TIME * 1000))
    }

    f = open(os.path.join(log_dir, "report.json"), "w")
    f.write(json.dumps(result))
    f.close()
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for proc in psutil.process_iter():
        if "FlightSimulator" in proc.name():
            proc.terminate()
    exit(1)
