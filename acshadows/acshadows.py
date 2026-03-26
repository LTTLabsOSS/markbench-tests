# pylint: disable=missing-module-docstring
import getpass
import logging
import re
import sys
import time
from pathlib import Path

import pydirectinput as user

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id

USERNAME = getpass.getuser()
STEAM_GAME_ID = 3159330
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "ACShadows.exe"

CONFIG_LOCATION = f"C:\\Users\\{USERNAME}\\Documents\\Assassin's Creed Shadows"
CONFIG_FILENAME = "ACShadows.ini"

user.FAILSAFE = False


def read_current_resolution():
    """Reads resolutions settings from local game file."""
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


def delete_videos() -> None:
    """Delete intro videos."""
    base_dir = Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Assassin's Creed Shadows"
    )
    videos_dir = base_dir / "videos"
    videos_en_dir = videos_dir / "en"
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


def move_benchmark_file() -> None:
    """Move html benchmark results to log folder."""
    src_dir = Path(
        f"C:\\Users\\{USERNAME}\\Documents\\Assassin's Creed Shadows\\benchmark_reports"
    )
    for src_path in src_dir.iterdir():
        dest_path = LOG_DIRECTORY / src_path.name
        if src_path.is_file():
            try:
                src_path.rename(dest_path)
                logging.info("Benchmark HTML moved")
            except Exception as e:
                logging.error("Failed to move %s: %s", src_path, e)
        else:
            logging.error("Benchmark HTML not found.")


def launch_game() -> None:
    """Handle pre-launch setup and game launch."""
    delete_videos()
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run the benchmark."""
    launch_game()
    time.sleep(15)

    if find_word("hardware", timeout=30, interval=1):
        user.mouseDown()
        time.sleep(0.2)
        press("space")

    if not find_word("animus", timeout=130, interval=1, msg="did not find main menu"):
        return FAILED_RUN

    setup_start_time = int(time.time())
    press("f1")

    if not find_word("system", msg="Couldn't find 'System' button"):
        return FAILED_RUN

    press("down, space")

    if not find_word(
        "benchmark",
        msg="couldn't find 'benchmark' on screen before settings",
    ):
        return FAILED_RUN

    press("space")
    time.sleep(1)
    am.take_screenshot("01_display_1.png", ArtifactType.CONFIG_IMAGE)
    press("down*13")
    am.take_screenshot("02_display_2.png", ArtifactType.CONFIG_IMAGE)
    press("down*4")
    am.take_screenshot("03_display_3.png", ArtifactType.CONFIG_IMAGE)
    press("c")
    time.sleep(1)
    am.take_screenshot("04_scalability_1.png", ArtifactType.CONFIG_IMAGE)
    press("down*10")
    am.take_screenshot("05_scalability_2.png", ArtifactType.CONFIG_IMAGE)
    press("down*6")
    am.take_screenshot("06_scalability_3.png", ArtifactType.CONFIG_IMAGE)
    press("down*5")
    am.take_screenshot("07_scalability_4.png", ArtifactType.CONFIG_IMAGE)
    press("esc")

    if not find_word(
        "benchmark",
        msg="couldn't find 'benchmark' on screen after settings",
    ):
        return FAILED_RUN

    press("down, space")
    logging.info("Setup took %d seconds", int(time.time()) - setup_start_time)

    if not find_word("benchmark", timeout=50, interval=1, msg="did not find benchmark"):
        return FAILED_RUN

    test_start_time = int(time.time())
    time.sleep(100)

    if not find_word("results", timeout=60, msg="did not find results screen"):
        return FAILED_RUN

    test_end_time = int(time.time()) - 2
    logging.info("Benchmark took %d seconds", test_end_time - test_start_time)
    am.take_screenshot("08_results.png", ArtifactType.RESULTS_IMAGE)
    press("x")
    time.sleep(5)
    press("esc")
    move_benchmark_file()
    time.sleep(5)
    return test_start_time, test_end_time


def main() -> None:
    """Run the Assassin's Creed Shadows benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = read_current_resolution()
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
            }
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        exit_code = 1
    finally:
        terminate_processes(PROCESS_NAME)
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
