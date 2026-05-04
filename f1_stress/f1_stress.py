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

from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
    exec_steam_game,
    get_build_id,
)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
STEAM_GAME_ID = 2488620
PROCESS_NAME = "F1_24.exe"
CONFIG_FILENAME = "hardware_settings_config.xml"
TOML_CONFIG = SCRIPT_DIRECTORY / "f1_stress.toml"
HARDWARE_SETTINGS_SOURCE = (
    SCRIPT_DIRECTORY / "config" / "hardwaresettings" / CONFIG_FILENAME
)
USERNAME = getpass.getuser()
HARDWARE_SETTINGS_DIRECTORY = Path(
    f"C:\\Users\\{USERNAME}\\Documents\\My Games\\F1 24\\hardwaresettings"
)


def get_benchmark_options() -> tuple[list[str], str]:
    """Read benchmark choices from the harness TOML."""
    with open(TOML_CONFIG, "rb") as config_file:
        config = tomllib.load(config_file)

    for arg in config.get("args", []):
        if arg.get("name") != "benchmark":
            continue

        values = arg.get("values", [])
        default = arg.get("default", values[0] if values else None)
        if not values:
            raise ValueError("No benchmark values configured in f1_stress.toml")
        if default not in values:
            raise ValueError("Default benchmark is not listed in f1_stress.toml")
        return values, default

    raise ValueError("Benchmark select arg not found in f1_stress.toml")


def get_args(benchmark_values: list[str], default_benchmark: str):
    """Returns command line arg values."""
    parser = ArgumentParser()
    parser.add_argument(
        "--benchmark",
        dest="benchmark",
        help="Benchmark XML file to run",
        choices=benchmark_values,
        default=default_benchmark,
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


def prepare_hardware_settings() -> Path:
    """Copy static hardware settings to F1's My Games directory."""
    source_file = HARDWARE_SETTINGS_SOURCE.resolve()
    destination_file = HARDWARE_SETTINGS_DIRECTORY / source_file.name

    if not source_file.is_file():
        logging.error("Hardware settings source not found: %s", source_file)
        sys.exit(1)

    HARDWARE_SETTINGS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    logging.info("Copying hardware settings: %s -> %s", source_file, destination_file)
    shutil.copy(source_file, destination_file)
    return destination_file


def run_benchmark(duration_seconds: int, benchmark_file: Path) -> tuple[float, float]:
    """Launch F1 24 benchmark mode and run until duration elapses."""
    logging.info("Stress duration: %d seconds", duration_seconds)
    logging.info("Launching F1 24 with benchmark XML: %s", benchmark_file)

    start_time = time.time()
    exec_steam_game(
        STEAM_GAME_ID,
        game_params=["-benchmark", str(benchmark_file.resolve())],
    )
    time.sleep(duration_seconds)

    logging.info("Stress duration reached. Terminating F1 24.")
    terminate_processes(PROCESS_NAME)
    end_time = time.time()

    return start_time, end_time


def main():
    """Entry point."""
    setup_logging(LOG_DIRECTORY)
    benchmark_values, default_benchmark = get_benchmark_options()
    missing_benchmarks = [
        str((SCRIPT_DIRECTORY / benchmark).resolve())
        for benchmark in benchmark_values
        if not (SCRIPT_DIRECTORY / benchmark).resolve().is_file()
    ]
    if missing_benchmarks:
        logging.error("Configured benchmark XML not found: %s", missing_benchmarks)
        sys.exit(1)

    args = get_args(benchmark_values, default_benchmark)

    benchmark_file = (SCRIPT_DIRECTORY / args.benchmark).resolve()
    prepare_hardware_settings()

    start_time, end_time = run_benchmark(args.duration_seconds, benchmark_file)

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
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
