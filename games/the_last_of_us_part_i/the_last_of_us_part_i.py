"""The Last of Us Part I test script"""

import logging
import re
import shutil
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    create_artifacts_manifest,
)
from harness_utils.input import mangohud_log_toggle, press, user
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, user_saved_games
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.screenshot import capture_screenshot_array
from harness_utils.steam import (
    exec_steam_game,
    get_active_steam_account_id,
)

logger = logging.getLogger(__name__)

STEAM_GAME_ID = 1888930
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "tlou-i.exe"

user.FAILSAFE = False


def read_resolution_from_config(config_path: Path) -> tuple[int, int]:
    """Read the configured resolution, falling back to the native display size."""
    window_mode_pattern = re.compile(r"WindowMode=(\d)")
    with config_path.open(encoding="utf-8") as config_file:
        window_mode_match = window_mode_pattern.search(config_file.readline())
        if window_mode_match is None:
            raise ValueError(f"WindowMode not found in {config_path}")

        if int(window_mode_match.group(1)) == 1:
            width_pattern = re.compile(r"BorderlessWidth=(\d+)")
            height_pattern = re.compile(r"BorderlessHeight=(\d+)")
        else:
            width_pattern = re.compile(r"WindowWidth=(\d+)")
            height_pattern = re.compile(r"WindowHeight=(\d+)")

        width = 0
        height = 0
        for line in config_file:
            width_match = width_pattern.search(line)
            height_match = height_pattern.search(line)
            if width_match is not None:
                width = int(width_match.group(1))
            if height_match is not None:
                height = int(height_match.group(1))

    if width == 0 or height == 0:
        screenshot = capture_screenshot_array()
        if screenshot is None:
            raise RuntimeError("Could not determine the native display resolution")
        native_height, native_width = screenshot.shape[:2]
        if width == 0:
            width = native_width
        if height == 0:
            height = native_height

    return height, width


def copy_autosave(steam_account_id: int) -> None:
    """Replace the active user's autosave with the benchmark save."""
    source = SCRIPT_DIRECTORY / "SAVEFILE0A"
    save_data_directory = (
        user_saved_games(STEAM_GAME_ID)
        / "The Last of Us Part I"
        / "users"
        / str(steam_account_id)
        / "SaveData"
    )
    destination = save_data_directory / source.name

    if not source.exists():
        raise FileNotFoundError(f"Source autosave folder not found: {source}")

    save_data_directory.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
        logger.info("Removing old save file")

    time.sleep(10)
    shutil.copytree(source, destination)
    logger.info("Autosave copied from %s -> %s", source, destination)


def take_screenshots() -> None:
    """Take screenshots of the benchmark settings"""

    logger.info("Taking screenshots of benchmark settings")

    # navigating to the display menu
    result = find_word("options", interval=1, timeout=5)
    if not result:
        logger.info("Did not see main menu. Did something mess up?")
        sys.exit(1)
    press("s*2,enter")

    result = find_word("display", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see options menu (looking for display). Did something mess up?"
        )
        sys.exit(1)
    press("s*4,enter")
    # taking the display menu screenshots
    result = find_word("aspect", interval=1, timeout=5)
    if not result:
        logger.info("Did not see aspect ratio setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video1.png")
    press("s*14")
    result = find_word("safezone", interval=1, timeout=5)
    if not result:
        logger.info("Did not see safezone scale setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video2.png")
    press("s*7")
    result = find_word("gore", interval=1, timeout=5)
    if not result:
        logger.info("Did not see gore setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video3.png")

    # navigating to the graphics menu
    press("backspace")
    result = find_word("graphics", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see options menu (looking for graphics). Did something mess up?"
        )
        sys.exit(1)
    press("s,enter")
    # taking the graphics screenshots
    result = find_word("preset", interval=1, timeout=5)
    if not result:
        logger.info("Did not see graphics preset setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics1.png")
    press("s*10")
    result = find_word("sampling", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see texture sampling quality setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics2.png")
    press("s*7")
    result = find_word("point", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see point lights shadow resolution setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics3.png")
    press("s*8")
    result = find_word("tracing", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see screen space cone tracing setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics4.png")
    press("s*7")
    result = find_word("scattering", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see screen space sub-surface scattering setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics5.png")
    press("s*6")
    result = find_word("bloom", interval=1, timeout=5)
    if not result:
        logger.info("Did not see bloom resolution setting. Did something mess up?")
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics6.png")
    press("s*6")
    result = find_word("ambient", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see ambient character density setting. Did something mess up?"
        )
        sys.exit(1)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "graphics7.png")
    time.sleep(0.5)

    # navigating back to main menu
    press("backspace*2")
    result = find_word("behind", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not see main menu after taking the graphics screenshots. Did something mess up?"
        )
        sys.exit(1)


def navigate_main_menu(steam_account_id: int) -> None:
    """Input to navigate main menu"""
    logger.info("Navigating main menu")

    take_screenshots()

    # Copy the autosave here
    copy_autosave(steam_account_id)
    time.sleep(5)

    # navigating to the load menu
    press("w*2,space")
    result = find_word("load", interval=1, timeout=5)
    if not result:
        logger.info("Did not see story menu. Did something mess up?")
        sys.exit(1)

    # Press load game
    press("s*2,space")
    # Verify in the load section
    result = find_word("hometown", interval=1, timeout=5)
    if not result:
        logger.info(
            "Did not saves to load. Did something mess up? Or did you forget to delete the saves?"
        )
        sys.exit(1)

    # load the save
    press("space")


def run_benchmark(steam_account_id: int):
    """Starts the benchmark"""
    exec_steam_game(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    time.sleep(30)

    result = find_word("press", interval=5, timeout=120)
    if not result:
        logger.info("Did not see start screen")
        sys.exit(1)

    time.sleep(1)

    press("space")
    time.sleep(1)
    navigate_main_menu(steam_account_id)

    # press load save
    result = find_word("yes", timeout=10, interval=1)
    if not result:
        logger.info("Did not load the save")
        sys.exit(1)

    press("a,space")
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)

    result = find_word("tommy", interval=0.2, timeout=250)
    if not result:
        logger.info("Did not see Tommy's first subtitle. Did the game load?")
        sys.exit(1)
    test_start_time = int(time.time())
    logger.info("Saw Tommy's first line. Benchmark has started.")

    # wait for black screen
    time.sleep(150)

    # This actually looks for "from?" but the current ML model sees it as fromy
    result = find_word("from", interval=0.2, timeout=250)
    if not result:
        logger.info("Did not find prompt to end harness.")
        sys.exit(1)

    # Wait for black screen
    time.sleep(24)

    test_end_time = int(time.time())

    time.sleep(2)
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)

    terminate_process(PROCESS_NAME)

    logger.info("Sleeping to let steam cloud catch up as to avoid overriding.")
    time.sleep(10)

    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

try:
    steam_account_id = get_active_steam_account_id()
    start_time, end_time = run_benchmark(steam_account_id)
    config_path = (
        user_saved_games(STEAM_GAME_ID)
        / "The Last of Us Part I"
        / "users"
        / str(steam_account_id)
        / "screeninfo.cfg"
    )

    height, width = read_resolution_from_config(config_path)
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }
    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)

except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    terminate_process(PROCESS_NAME)
    sys.exit(1)
