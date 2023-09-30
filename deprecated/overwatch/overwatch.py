"""Overwatch test script"""
import json
import logging
import os
import re
import shutil
import sys
import time
import winreg
from argparse import ArgumentParser
from subprocess import Popen

import psutil
import pyautogui as gui
import pydirectinput as user
from dotenv import load_dotenv
from overwatch_utils import templates

# pylint: disable=wrong-import-position
sys.path.append("..")
import deprecated.cv2_utils

# pylint: enable=wrong-import-position

load_dotenv(override=True)

HEIGHT_PATTERN = r"FullScreenHeight = \"(\d*)\""
WIDTH_PATTERN = r"FullScreenWidth = \"(\d*)\""
DEFAULT_INSTALLATION_PATH = "C:\\Program Files (x86)\\Overwatch\\_retail_"
EXECUTABLE = "Overwatch.exe"
WORKSHOP_CODE = "HYT6F"  # same code Nvidia uses
CACHE_DIRECTORIES = [
    "C:\\ProgramData\\Blizzard Entertainment",
    "C:\\ProgramData\\Battle.net",
]


def get_documents_path():
    """Gets registry key of documents path."""
    shell_folder_key = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    )
    try:
        root_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        shell_folders_handle = winreg.OpenKeyEx(root_handle, shell_folder_key)
        personal_path_key = winreg.QueryValueEx(shell_folders_handle, "Personal")
        return personal_path_key[0]
    finally:
        root_handle.Close()


def get_settings_path() -> str:
    """Returns string path to game settings ini file."""
    return f"{get_documents_path()}\\Overwatch\\Settings\\Settings_v0.ini"


def read_current_resolution():
    """Reads resolution from local settings file."""
    hpattern = re.compile(HEIGHT_PATTERN)
    wpattern = re.compile(WIDTH_PATTERN)
    width = 0
    height = 0
    with open(get_settings_path(), encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            result = hpattern.match(line)
            if result is not None:
                height = result.group(1)

            result2 = wpattern.match(line)
            if result2 is not None:
                width = result2.group(1)
            if int(h) > 0 and int(w) > 0:
                break
    return (width, height)


def start_game():
    """Starts game executable."""
    cmd = DEFAULT_INSTALLATION_PATH + "\\" + EXECUTABLE
    logging.info(cmd)
    return Popen(cmd)


def send_input(string):
    """Sends series of key presses"""
    for char in string:
        gui.press(char)


def run_benchmark(username, password):
    """Runs the actual game benchmark"""
    start_game()
    time.sleep(15)

    # Login
    send_input(username)
    user.press("tab")
    send_input(password)
    user.press("tab")
    user.press("enter")

    # Get into play game menu
    time.sleep(15)  # wait for login menu to authenticate
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

    deprecated.cv2_utils.wait_for_image_on_screen(
        "start_button", interval=15, timeout=360
    )

    for process in psutil.process_iter():
        if "Overwatch" in process.name():
            process.terminate()


script_dir = os.path.dirname(os.path.realpath(__file__))

log_dir = os.path.join(script_dir, "run")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)

LOGGING_FORMAT = "%(asctime)s %(levelname)-s %(message)s"
logging.basicConfig(
    filename=f"{log_dir}/harness.log",
    format=LOGGING_FORMAT,
    datefmt="%m-%d %H:%M",
    level=logging.DEBUG,
)
console = logging.StreamHandler()
formatter = logging.Formatter(LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

parser = ArgumentParser()
parser.add_argument(
    "-u",
    "--username",
    dest="username",
    help="username",
    metavar="username",
    required=True,
)
parser.add_argument(
    "-c",
    "--password",
    dest="password",
    help="password",
    metavar="password",
    required=True,
)
args = parser.parse_args()

try:
    deprecated.cv2_utils.templates = templates
    for cache in CACHE_DIRECTORIES:
        try:
            shutil.rmtree(cache)
        except OSError as e:
            logging.warning("Couldn't delete %s: %s", cache, e)
    run_benchmark(args.username, args.password)
    w, h = read_current_resolution()
    report = {
        "resolution": f"{w}x{h}",
    }

    with open(
        os.path.join(log_dir, "report.json"), "w", encoding="utf-8"
    ) as report_file:
        report_file.write(json.dumps(report))

# pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for proc in psutil.process_iter():
        if "Overwatch" in proc.name():
            proc.terminate()
    sys.exit(1)
