# pylint: disable=missing-module-docstring
import logging
from pathlib import Path
import time
import sys
import re
import pydirectinput as user
import getpass
sys.path.insert(1, str(Path(sys.path[0]).parent))

# pylint: disable=wrong-import-position
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_logging,
    write_report_json,
    seconds_to_milliseconds,
)
from harness_utils.steam import get_build_id, exec_steam_game
from harness_utils.keras_service import KerasService
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import (
    press_n_times,
    int_time,
    find_word,
    keras_args)

USERNAME = getpass.getuser()
STEAM_GAME_ID = 3159330
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
PROCESS_NAME = "ACShadows.exe"

CONFIG_LOCATION = f"C:\\Users\\{USERNAME}\\Documents\\Assassin's Creed Shadows"
CONFIG_FILENAME = "ACShadows.ini"

user.FAILSAFE = False


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"FullscreenWidth=(\d+)")
    width_pattern = re.compile(r"FullscreenHeight=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


def delete_videos():
    """deletes intro videos"""
    base_dir = Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Assassin's Creed Shadows")
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
        videos_en_dir / "WarningSaving.webm"
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
        r"C:\Users\Administrator\Documents\Assassin's Creed Shadows\benchmark_reports")

    for src_path in src_dir.iterdir():
        dest_path = LOG_DIR / src_path.name

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


def navi_settings(am):
    """navigates and takes pictures of settings"""
    user.press("space")

    time.sleep(1)

    am.take_screenshot(
        "display1.png", ArtifactType.CONFIG_IMAGE, "display settings 1")

    press_n_times("down", 13, 0.3)

    am.take_screenshot(
        "display2.png", ArtifactType.CONFIG_IMAGE, "display settings 2")

    press_n_times("down", 4, 0.3)

    am.take_screenshot(
        "display3.png", ArtifactType.CONFIG_IMAGE, "display settings 3")

    user.press("c")

    time.sleep(1)

    am.take_screenshot(
        "scalability1.png", ArtifactType.CONFIG_IMAGE,
        "scalability settings 1")

    press_n_times("down", 10, 0.3)

    am.take_screenshot(
        "scalability2.png", ArtifactType.CONFIG_IMAGE,
        "scalability settings 2")

    press_n_times("down", 6, 0.3)

    am.take_screenshot(
        "scalability3.png", ArtifactType.CONFIG_IMAGE,
        "scalability settings 3")

    press_n_times("down", 5, 0.3)

    am.take_screenshot(
        "scalability4.png", ArtifactType.CONFIG_IMAGE,
        "scalability settings 4")

    user.press("esc")


def run_benchmark(keras_service):
    """runs the benchmark"""
    delete_videos()
    start_game()
    setup_start_time = int_time()
    am = ArtifactManager(LOG_DIR)
    time.sleep(30)

    if keras_service.wait_for_word(
            word="animus", timeout=130, interval=1) is None:
        logging.info("did not find main menu")
        sys.exit(1)

    user.press("f1")

    find_word(keras_service, "system", "Couldn't find 'System' button")

    user.press("down")

    time.sleep(1)

    user.press("space")

    find_word(
        keras_service, "benchmark",
        "couldn't find 'benchmark' on screen before settings")

    navi_settings(am)

    find_word(
        keras_service, "benchmark",
        "couldn't find 'benchmark' on screen after settings")

    user.press("down")

    time.sleep(1)

    user.press("space")

    setup_end_time = int_time()
    elapsed_setup_time = setup_end_time - setup_start_time
    logging.info("Setup took %d seconds", elapsed_setup_time)

    if keras_service.wait_for_word(
            word="benchmark", timeout=50, interval=1) is None:
        logging.info("did not find benchmark")
        sys.exit(1)

    test_start_time = int_time()

    time.sleep(100)

    find_word(keras_service, "results", "did not find results screen", 60)

    test_end_time = int_time() - 2

    elapsed_test_time = test_end_time - test_start_time
    logging.info("Benchmark took %d seconds", elapsed_test_time)

    am.take_screenshot(
        "benchmark_results.png", ArtifactType.RESULTS_IMAGE,
        "benchmark results")

    user.press("x")

    time.sleep(5)

    user.press("esc")

    move_benchmark_file()

    time.sleep(5)

    terminate_processes(PROCESS_NAME)

    am.create_manifest()

    return test_start_time, test_end_time


def main():
    """entry point"""
    keras_service = KerasService(
        keras_args().keras_host, keras_args().keras_port)
    start_time, endtime = run_benchmark(keras_service)
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID)
    }
    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging(LOG_DIR)
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
