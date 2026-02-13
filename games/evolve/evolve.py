"""Evolve test script"""

import csv
import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil

sys.path.insert(1, str((Path(sys.path[0]) / "../..").resolve()))

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.process import is_process_running

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
EVOLVE_DIR = Path(r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Evolve")
EXECUTABLE = "evolve.exe"
EXECUTABLE_PATH = EVOLVE_DIR / EXECUTABLE
RESULTS_FILE = LOG_DIR / "evolve-results.csv"


def setup_logging():
    """default logging config"""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=f"{LOG_DIR}/harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


TRACE_MODES = ["inline", "pipeline", "work-graph"]
RENDERERS = ["ray-tracing", "path-tracing"]
PRESETS = ["ultra", "high", "medium"]
RESOLUTIONS = [(1920, 1080), (2560, 1440), (3840, 2160)]


def get_scores(results_path):
    """obtain and parse the scores from the evolve run"""
    with open(results_path, mode="r", encoding="utf-8") as results_file:
        # Format is score name in the first row,
        # score on the second row, which DictReader
        # will translate to a proper dict.
        # Only a single loop so only return the
        # first result
        results = list(csv.DictReader(results_file))[0]
    return results


def launch_evolve(resolution, renderer, trace_mode, preset):
    """launch evolve with the given render and trace parameters"""
    launch_command = f'"{EXECUTABLE_PATH}"  --offline run-custom --render-resolution {resolution[0]} {resolution[1]} --renderer {renderer} --mode {trace_mode} --preset {preset} --fullscreen --export-scores {RESULTS_FILE}'
    with subprocess.Popen(
        launch_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=(EVOLVE_DIR),
    ) as proc:
        logging.info("Evolve has started.")
        start_time = time.time()
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 30:  # seconds
                raise ValueError("Evolve Benchmark subprocess did not start in time")
            process = is_process_running(EXECUTABLE)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)
        _, _ = proc.communicate()  # blocks until Evolve exits
        return proc


def main():
    """a doc string"""
    setup_logging()
    parser = ArgumentParser()

    parser.add_argument(
        "--resolution",
        help="The resolution of the rendered image",
        required=True,
        nargs=2,
        type=int,
    )

    parser.add_argument(
        "--renderer",
        help="Whether to run with the hybrid renderer or path tracer",
        required=True,
        choices=RENDERERS,
    )

    parser.add_argument(
        "--trace-mode",
        help="Which type of hardware accelerated ray-tracing mode should be used",
        required=True,
        choices=TRACE_MODES,
    )

    parser.add_argument(
        "--preset",
        help="The graphics settings preset to use",
        required=True,
        choices=PRESETS,
    )

    args = parser.parse_args()

    logging.info(
        "Starting Evolve: \nResolution: %s\nRenderer: %s\nTrace Mode: %s\nPreset: %s",
        args.resolution,
        args.renderer,
        args.trace_mode,
        args.preset,
    )

    start_time = time.time()
    launch_evolve(args.resolution, args.renderer, args.trace_mode, args.preset)
    end_time = time.time()
    scores = get_scores(RESULTS_FILE)
    logging.info("Benchmark took %.2f seconds", end_time - start_time)

    report = {
        "test": "Evolve Benchmark",
        "test_parameter": f"{args.renderer} {args.trace_mode} {args.preset}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "unit": "Score",
        "Raytracing": scores["Raytracing"],
        "Acceleration Structure Builds": scores["Acceleration Structure Builds"],
        "Rasterization": scores["Rasterization"],
        "Compute": scores["Compute"],
        "Workgraphs": scores["Workgraphs"],
        "Driver": scores["Driver"],
        "Energy": scores["Energy"],
    }

    write_report_json(str(LOG_DIR), "report.json", report)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logging.error("something went wrong running the benchmark!")
        logging.exception(ex)
        sys.exit(1)
