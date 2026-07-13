"""F1 24 stress test script."""

import getpass
import logging
import shutil
import sys
import time
import tomllib
from argparse import ArgumentParser
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.ocr_service import find_word
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_process
from harness_utils.steam import (
    exec_steam_game,
    get_app_install_location,
    get_build_id,
)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
STEAM_GAME_ID = 2488620
PROCESS_NAME = "F1_24.exe"
CONFIG_FILENAME = "hardware_settings_config.xml"
BENCHMARK_FILENAME = "canada_5_loop.xml"
TOML_CONFIG = SCRIPT_DIRECTORY / "f1_stress.toml"
BENCHMARK_DIRECTORY = SCRIPT_DIRECTORY / "benchmarks"
BENCHMARK_FILE = BENCHMARK_DIRECTORY / BENCHMARK_FILENAME
HARDWARE_SETTINGS_SOURCE_DIRECTORY = SCRIPT_DIRECTORY / "hardware_settings"
USERNAME = getpass.getuser()
HARDWARE_SETTINGS_DIRECTORY = Path(
    f"C:\\Users\\{USERNAME}\\Documents\\My Games\\F1 24\\hardwaresettings"
)


def get_select_options(arg_name: str) -> tuple[list[str], str]:
    """Read select choices from the harness TOML."""
    with open(TOML_CONFIG, "rb") as config_file:
        config = tomllib.load(config_file)

    for arg in config.get("args", []):
        if arg.get("name") != arg_name:
            continue

        values = arg.get("values", [])
        default = arg.get("default", values[0] if values else None)
        if not values:
            raise ValueError(f"No {arg_name} values configured in f1_stress.toml")
        if default not in values:
            raise ValueError(f"Default {arg_name} is not listed in f1_stress.toml")
        return values, default

    raise ValueError(f"{arg_name} select arg not found in f1_stress.toml")


def get_args(
    hardware_settings_values: list[str],
    default_hardware_settings: str,
):
    """Returns command line arg values."""
    parser = ArgumentParser()
    parser.add_argument(
        "--hardware-settings",
        "--hardware_settings",
        dest="hardware_settings",
        help="Hardware settings XML file to apply",
        choices=hardware_settings_values,
        default=default_hardware_settings,
    )
    parser.add_argument(
        "--duration-seconds",
        "--duration_seconds",
        dest="duration_seconds",
        help="Stress duration in seconds",
        type=int,
        default=900,
    )
    return parser.parse_args()


def find_missing_files(directory: Path, filenames: list[str]) -> list[str]:
    """Return configured files missing from a source directory."""
    return [
        str((directory / filename).resolve())
        for filename in filenames
        if not (directory / filename).resolve().is_file()
    ]


def prepare_hardware_settings(hardware_settings_file: Path) -> Path:
    """Copy selected hardware settings to F1's My Games directory."""
    destination_file = HARDWARE_SETTINGS_DIRECTORY / CONFIG_FILENAME
    HARDWARE_SETTINGS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    logging.info(
        "Copying hardware settings: %s -> %s",
        hardware_settings_file,
        destination_file,
    )
    shutil.copy(hardware_settings_file, destination_file)
    return destination_file


def prepare_benchmark_file() -> Path:
    """Copy the hardcoded benchmark XML to F1's benchmark folder."""
    destination_directory = Path(get_app_install_location(STEAM_GAME_ID)) / "benchmark"
    destination_file = destination_directory / BENCHMARK_FILENAME
    destination_directory.mkdir(parents=True, exist_ok=True)
    logging.info("Copying benchmark XML: %s -> %s", BENCHMARK_FILE, destination_file)
    shutil.copy(BENCHMARK_FILE, destination_file)
    return destination_file


def run_benchmark(
    duration_seconds: int,
    benchmark_filename: str,
) -> tuple[float, float]:
    """Launch F1 24 benchmark mode and run until duration elapses."""
    logging.info("Stress duration: %d seconds", duration_seconds)
    logging.info("Launching F1 24 with benchmark XML: %s", benchmark_filename)

    exec_steam_game(
        STEAM_GAME_ID,
        game_params=["-benchmark", benchmark_filename],
    )

    time.sleep(10)

    result = find_word("fps", interval=0, timeout=90)
    if result is None:
        logging.error("FPS counter was not found. Could not mark stress start time.")
        terminate_process(PROCESS_NAME)
        sys.exit(1)

    logging.info("Found FPS counter. Starting stress timer.")
    start_time = time.time()
    time.sleep(duration_seconds)

    logging.info("Stress duration reached. Terminating F1 24.")
    terminate_process(PROCESS_NAME)
    end_time = time.time()

    return start_time, end_time


def main():
    """Entry point."""
    setup_logging(LOG_DIRECTORY)
    hardware_settings_values, default_hardware_settings = get_select_options(
        "hardware_settings"
    )

    if not BENCHMARK_FILE.resolve().is_file():
        logging.error("Benchmark XML not found: %s", BENCHMARK_FILE.resolve())
        sys.exit(1)

    missing_hardware_settings = find_missing_files(
        HARDWARE_SETTINGS_SOURCE_DIRECTORY, hardware_settings_values
    )
    if missing_hardware_settings:
        logging.error(
            "Configured hardware settings XML not found: %s",
            missing_hardware_settings,
        )
        sys.exit(1)

    args = get_args(
        hardware_settings_values,
        default_hardware_settings,
    )

    hardware_settings_file = (
        HARDWARE_SETTINGS_SOURCE_DIRECTORY / args.hardware_settings
    ).resolve()
    prepare_hardware_settings(hardware_settings_file)
    prepare_benchmark_file()

    start_time, end_time = run_benchmark(
        args.duration_seconds,
        BENCHMARK_FILENAME,
    )

    report = {
        "test": "F1 24 Stress",
        "stress_duration_seconds": args.duration_seconds,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }
    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_process(PROCESS_NAME)
        sys.exit(1)
