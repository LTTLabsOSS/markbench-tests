import json
import logging
import os
import re
import tempfile
import time
import winreg
from argparse import ArgumentParser
from subprocess import Popen
import shutil
from dotenv import load_dotenv
from cv2_utils import *

load_dotenv(override=True)

import psutil
import pyautogui as gui
import pydirectinput as user

# TODO:
# - Find installation
# - Set configuration 
# - Use proper template pattern for 16x9 and 16x10

# RenderScale = "100"

PRESET_PATTERN = r"GFXPresetLevel = \"(\d*)\""
RENDER_SCALE_PATTERN = r"RenderScale = \"(\d*)\""
HEIGHT_PATTERN = r"FullScreenHeight = \"(\d*)\""
WIDTH_PATTERN = r"FullScreenWidth = \"(\d*)\""
WINDOW_MODE_PATTERN = r"WindowMode = \"(\d*)\""
FULLSCREEN_WINDOW_PATTERN = r"FullscreenWindow = \"(\d*)\""
FULLSCREEN_WINDOW_ENABLED_PATTERN = r"FullscreenWindowEnabled = \"(\d*)\""

SETTINGS_PATH = "C:\\Users\\Nikolas\\Documents\\Overwatch\\Settings\\Settings_v0.ini"
DEFAULT_INSTALLATION_PATH = "C:\\Program Files (x86)\\Overwatch\\_retail_" # default path when installed to C:/
#DEFAULT_INSTALLATION_PATH = "E:\Bnet\Overwatch\_retail_" # Nik's path at home
EXECUTABLE = "Overwatch.exe"

WORKSHOP_CODE = "HYT6F" # same code Nvidia uses

CACHE_DIRECTORIES = [
    "C:\\ProgramData\\Blizzard Entertainment",
    "C:\\ProgramData\\Battle.net"
]

def sed_inplace(filename, pattern, repl):
    '''
    Perform of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    See https://stackoverflow.com/a/31499114
    '''
    pattern_compiled = re.compile(pattern)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


def mydocumentspath():
    SHELL_FOLDER_KEY = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    try:
        root_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        shell_folders_handle = winreg.OpenKeyEx(root_handle, SHELL_FOLDER_KEY)
        personal_path_key = winreg.QueryValueEx(shell_folders_handle, 'Personal')
        return personal_path_key[0]
    finally:
        root_handle.Close()


SETTINGS_PATH = f"{mydocumentspath()}\\Overwatch\\Settings\\Settings_v0.ini"

def read_current_resolution():
    hpattern = re.compile(HEIGHT_PATTERN)
    wpattern = re.compile(WIDTH_PATTERN)
    h = w = 0
    with open(SETTINGS_PATH) as fp:
        lines = fp.readlines()
        for line in lines:
            result = hpattern.match(line)
            if result is not None:
                h = result.group(1)

            result2 = wpattern.match(line)
            if result2 is not None:
                w = result2.group(1)
            if int(h) > 0 and int(w) > 0:
                break
    return (h, w)


preset_mapping = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "ultra": 4,
    "epic": 5
}

def set_preset(preset):
    if preset not in preset_mapping:
        raise Exception(f"Unrecognized preset {preset}")
    replace_string = f"GFXPresetLevel = \"{preset_mapping[preset]}\""
    sed_inplace(SETTINGS_PATH, PRESET_PATTERN, replace_string)


def set_window_defaults():
    '''Set options to full screen'''
    sed_inplace(SETTINGS_PATH, WINDOW_MODE_PATTERN, "WindowMode = \"0\"")
    sed_inplace(SETTINGS_PATH, FULLSCREEN_WINDOW_ENABLED_PATTERN, "FullscreenWindowEnabled = \"1\"")
    sed_inplace(SETTINGS_PATH, FULLSCREEN_WINDOW_PATTERN, "FullscreenWindow = \"1\"")


def set_resolution(h, w):
    sed_inplace(SETTINGS_PATH, HEIGHT_PATTERN, f"FullScreenHeight = \"{h}\"")
    sed_inplace(SETTINGS_PATH, WIDTH_PATTERN, f"FullScreenWidth = \"{w}\"")
    pass


def start_game():
    cmd = DEFAULT_INSTALLATION_PATH + '\\' + EXECUTABLE
    logging.info(cmd)
    return Popen(cmd)


def send_input(string):
    for char in string:
        gui.press(char)


def run_benchmark(username, password):
    game_process = start_game()
    t1 = time.time()
    time.sleep(15)

    # Login
    send_input(username)
    user.press("tab")
    send_input(password)
    user.press("tab")
    user.press("enter")

    # Get into play game menu
    time.sleep(15) # wait for login menu to authenticate
    user.press("down")
    time.sleep(1)
    user.press("space")

    # Get into custom game menu
    user.press("right")
    user.press("right")
    user.press("right")
    user.press("right")
    user.press("space")
    time.sleep(3) 

    # tab over to Create Game
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("space")
    time.sleep(3)

    # get into create game settings
    user.press("right")
    user.press("right")
    user.press("up")
    user.press("left")
    user.press("space")
    time.sleep(3)

    # import custom map settings
    user.press("tab")
    user.press("right")
    user.press("space")
    send_input(WORKSHOP_CODE)
    user.press("tab")
    user.press("right")
    user.press("space")
    time.sleep(3)

    # start the benchmark
    user.press("escape")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("space")

    # give time for the benchmark to start 
    # and get into it before waiting for the lobby screen
    time.sleep(30) 

    wait_for_image_on_screen('start_button', DEFAULT_MATCH_THRESHOLD, interval=15, timeout=360)

    for proc in psutil.process_iter              ():
        if "Overwatch" in proc.name():
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

parser = ArgumentParser()
parser.add_argument("-p", "--preset", dest="preset",
                    help="graphics preset", metavar="preset", required=True)
parser.add_argument("-r", "--resolution", dest="resolution",
                    help="resolution", metavar="resolution", required=False)
parser.add_argument("-u", "--username", dest="username",
                    help="username", metavar="username", required=True)
parser.add_argument("-c", "--password", dest="password",
                    help="password", metavar="password", required=True)
args = parser.parse_args()


if args.preset:
    if args.preset == 'current':
        pass
    else:
        set_preset(args.preset)

if args.resolution:
    # expecting argument to be string "width,height"
    r = args.resolution.split(",")
    h = r[0]
    w = r[1]
    set_resolution(h, w)

try:
    for cache in CACHE_DIRECTORIES:
        try:
            shutil.rmtree(cache)
        except Exception as e:
            logging.warn(f"Couldn't delete {cache}: {e}")
    run_benchmark(args.username, args.password)
    h, w = read_current_resolution()
    result = {
        "resolution": f"{w}x{h}",
        "graphics_preset": args.preset
    }

    f = open(os.path.join(log_dir, "report.json"), "w")
    f.write(json.dumps(result))
    f.close()
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for proc in psutil.process_iter():
        if "Overwatch" in proc.name():
            proc.terminate()
    exit(1)
