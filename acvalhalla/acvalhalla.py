import json
from subprocess import Popen

import psutil
import os, stat
from arg_utils import read_args
from config_utils import ASS_CREED_FOLDER, CONFIG_FILENAME, load_preset, mydocumentspath, read_current_resolution, save_current_config
from cv2_utils import *

DEFAULT_INSTALLATION_PATH = "C:/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/games/Assassin's Creed Valhalla"
EXECUTABLE = "ACValhalla.exe"

def delete_vids():
    """
    Speed up the intro screen by deleting or renaming in /video folder:
    ANVIL_Logo.webm
    PC_AMD_Ryzen.webm
    UbisoftLogo.webm
    """
    vid1 = os.path.join(DEFAULT_INSTALLATION_PATH, "videos", "ANVIL_Logo.webm")
    vid2 = os.path.join(DEFAULT_INSTALLATION_PATH, "videos", "PC_AMD_Ryzen.webm")
    vid3 = os.path.join(DEFAULT_INSTALLATION_PATH, "videos", "UbisoftLogo.webm")
    vids = [vid1, vid2, vid3]
    for vid in vids:
        try:
            os.remove(vid)
        except:
            pass


def start_game():
    cmd = DEFAULT_INSTALLATION_PATH + '\\' + EXECUTABLE
    logging.info(cmd)
    return Popen(cmd)


def run_benchmark():
    game_process = start_game()
    t1 = time.time()

    ###
    # Wait for the intro screen to reach the "Press Any Key" title screen
    ###
    time.sleep(60)
    # wait_for_image_on_screen('press_any')
    user.press('enter')
    time.sleep(20)

    ###
    # Mercifully the benchmark button is right on the main screen, so push it!
    ###
    wait_and_click('benchmark', "run benchmark")
    user.press('enter')  # help it along if the click didn't work
    time.sleep(2)  # massage the menu loading
    wait_and_click('benchmark_confirmation', "confirm benchmark")
    time.sleep(1)
    user.press('space')

    t2 = time.time()
    logging.info(f"Setup took {round((t2 - t1), 2)} seconds")
    global START_TIME
    START_TIME = time.time()

    time.sleep(100) # sleep during benchmark, takes 90 + 10 grace seconds.

    # look for the results header
    logging.info("Test should be complete, looking for results page")
    wait_for_image_on_screen('results_header', DEFAULT_MATCH_THRESHOLD, interval=2, timeout=60)
    gui.screenshot(os.path.join(log_dir, "results.png"))
    global END_TIME
    END_TIME = time.time()
    logging.info(f"Benchark took {round((END_TIME - START_TIME), 2)} seconds")

    ###
    # Exit
    ###
    for proc in psutil.process_iter():
        if "ACValhalla" in proc.name():
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

args = read_args()

try:
    mydocuments = mydocumentspath()
    cfg = os.path.join(mydocuments, ASS_CREED_FOLDER, CONFIG_FILENAME)
    delete_vids()
    save_current_config(log_dir)
    run_benchmark()
    
    height, width = read_current_resolution()
    result = {
        "resolution": f"{width}x{height}",
        "start_time": round((START_TIME * 1000)), # seconds * 1000 = millis
        "end_time": round((END_TIME * 1000))
    }

    f = open(os.path.join(log_dir, "report.json"), "w")
    f.write(json.dumps(result))
    f.close()
except Exception as e:
    os.chmod(cfg, stat.S_IWRITE)
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for proc in psutil.process_iter():
        if "ACValhalla" in proc.name():
            proc.terminate()
    exit(1)
finally:
    os.chmod(cfg, stat.S_IWRITE)
