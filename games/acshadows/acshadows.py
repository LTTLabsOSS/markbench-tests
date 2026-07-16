import getpass
import logging
import re
import sys
import time
from pathlib import Path

import pydirectinput as user  # type: ignore[import-not-found]

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import reset_artifacts, save_screenshot
from harness_utils.paths import harness_directories
from harness_utils.input import press_n_times
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game, get_build_id

USERNAME = getpass.getuser()
STEAM_GAME_ID = 3159330
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "ACShadows.exe"

CONFIG_LOCATION = f"C:\\Users\\{USERNAME}\\Documents\\Assassin's Creed Shadows"
CONFIG_FILENAME = "ACShadows.ini"

user.FAILSAFE = False


def read_current_resolution() -> tuple[int, int]:
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"FullscreenWidth=(\d+)")
    width_pattern = re.compile(r"FullscreenHeight=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    try:
        with open(cfg, encoding="utf-8") as file:
            for line in file:
                height_match = height_pattern.search(line)
                width_match = width_pattern.search(line)
                if height_match is not None:
                    height_value = int(height_match.group(1))
                if width_match is not None:
                    width_value = int(width_match.group(1))
    except OSError:
        logging.exception("Failed to read resolution from %s", cfg)
        raise
    return (height_value, width_value)


def delete_videos():
    """deletes intro videos"""
    base_dir = Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Assassin's Creed Shadows"
    )
    videos_dir = base_dir / "videos"
    videos_en_dir = videos_dir / "en"

    # List of video files to delete
    videos_to_delete = [
        videos_dir / "ANVIL_Logo.webm",
        videos_dir / "INTEL_Logo.webm",
        videos_dir / "HUB_Bootflow_FranchiseIntro.webm",
        videos_dir / "HUB_Bootflow_AbstergoIntro.webm",
        videos_dir / "UbisoftLogo.webm",
        videos_en_dir / "Epilepsy.webm",
        videos_en_dir / "warning_disclaimer.webm",
        videos_en_dir / "WarningSaving.webm",
    ]

    for file_path in videos_to_delete:
        if file_path.exists():
            try:
                file_path.unlink()
                logging.info("Deleted: %s", file_path)
            except Exception as e:
                logging.error("Error deleting %s: %s", file_path, e)


def move_benchmark_file():
    """moves html benchmark results to log folder"""
    src_dir = Path(
        f"C:\\Users\\{USERNAME}\\Documents\\Assassin's Creed Shadows\\benchmark_reports"
    )

    for src_path in src_dir.iterdir():
        dest_path = ARTIFACTS_DIRECTORY / src_path.name

        if src_path.is_file():
            try:
                src_path.rename(dest_path)
                logging.info("Benchmark HTML moved")
            except Exception as e:
                logging.error("Failed to move %s: %s", src_path, e)
        else:
            logging.error("Benchmark HTML not found.")


def start_game():
    """Starts the game process"""
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")


def navi_settings():
    """navigates and takes pictures of settings"""
    user.press("space")

    time.sleep(1)

    save_screenshot(ARTIFACTS_DIRECTORY / "display1.png")

    press_n_times("down", 13, 0.3)

    save_screenshot(ARTIFACTS_DIRECTORY / "display2.png")

    press_n_times("down", 4, 0.3)

    save_screenshot(ARTIFACTS_DIRECTORY / "display3.png")

    user.press("c")

    time.sleep(1)

    save_screenshot(ARTIFACTS_DIRECTORY / "scalability1.png")

    press_n_times("down", 10, 0.3)

    save_screenshot(ARTIFACTS_DIRECTORY / "scalability2.png")

    press_n_times("down", 6, 0.3)

    save_screenshot(ARTIFACTS_DIRECTORY / "scalability3.png")

    press_n_times("down", 5, 0.3)

    save_screenshot(ARTIFACTS_DIRECTORY / "scalability4.png")

    user.press("esc")


def run_benchmark():
    """runs the benchmark"""
    delete_videos()
    start_game()
    setup_start_time = round(time.time())
    reset_artifacts(ARTIFACTS_DIRECTORY)
    time.sleep(15)

    if find_word(word="hardware", timeout=30, interval=1) is None:
        logging.info("did not find hardware")
    else:
        user.mouseDown()
        time.sleep(0.2)
        user.press("space")

    if find_word(word="animus", timeout=130, interval=1) is None:
        logging.info("did not find main menu")
        sys.exit(1)

    user.press("f1")

    if find_word("system", timeout=30, interval=1) is None:
        logging.error("Couldn't find 'System' button")
        sys.exit(1)

    user.press("down")

    time.sleep(1)

    user.press("space")

    if find_word("benchmark", timeout=30, interval=1) is None:
        logging.error("couldn't find 'benchmark' on screen before settings")
        sys.exit(1)

    navi_settings()

    if find_word("benchmark", timeout=30, interval=1) is None:
        logging.error("couldn't find 'benchmark' on screen after settings")
        sys.exit(1)

    user.press("down")

    time.sleep(1)

    user.press("space")

    setup_end_time = round(time.time())
    elapsed_setup_time = setup_end_time - setup_start_time
    logging.info("Setup took %d seconds", elapsed_setup_time)

    if find_word(word="benchmark", timeout=50, interval=1) is None:
        logging.info("did not find benchmark")
        sys.exit(1)

    test_start_time = round(time.time())

    time.sleep(100)

    if find_word("results", timeout=60, interval=1) is None:
        logging.error("did not find results screen")
        sys.exit(1)

    test_end_time = round(time.time()) - 2

    elapsed_test_time = test_end_time - test_start_time
    logging.info("Benchmark took %d seconds", elapsed_test_time)

    save_screenshot(ARTIFACTS_DIRECTORY / "results.png")

    user.press("x")

    time.sleep(5)

    user.press("esc")

    move_benchmark_file()

    time.sleep(5)

    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


def main():
    """entry point"""
    start_time, endtime = run_benchmark()
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID),
    }
    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging(LOG_DIRECTORY)
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_process(PROCESS_NAME)
        sys.exit(1)
