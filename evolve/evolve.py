"""Evolve test script"""

from pathlib import Path
from argparse import ArgumentParser
import logging
import os.path
import sys
import time
import subprocess
import psutil
import csv

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    write_report_json,
    seconds_to_milliseconds,
)
from harness_utils.process import (
    is_process_running
)


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


TRACE_MODES = ["pipeline", "inline", "workgraph"]
RENDERERS = ["ray-tracing", "path-tracing"]


def get_scores(results_path):
    """obtain and parse the scores from the evolve run"""
    with open(results_path, mode="r") as results_file:
        # Format is score name in the first row,
        # score on the second row, which DictReader
        # will translate to a proper dict.
        # Only a single loop so only return the
        # first result
        results = list(csv.DictReader(results_file))[0]
    return results


def launch_evolve(renderer, trace_mode):
    """launch evolve with the given render and trace parameters"""
    launch_command = f'"{EXECUTABLE_PATH}"  run-official --renderer {renderer} --mode {trace_mode} --export-scores {RESULTS_FILE}'
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
    setup_logging()
    parser = ArgumentParser()
    parser.add_argument(
        "-r",
        "--renderer",
        help="Whether to run with the hybrid renderer or path tracer",
        required=True,
        choices=RENDERERS,
    )
    parser.add_argument(
        "-t",
        "--trace-mode",
        help="Which type of hardware accelerated ray-tracing mode should be used",
        required=True,
        choices=TRACE_MODES,
    )
    args = parser.parse_args()

    logging.info(
        "Starting Evolve with %s renderer and trace mode %s",
        args.renderer,
        args.trace_mode,
    )

    start_time = time.time()
    launch_evolve(args.renderer, args.trace_mode)
    end_time = time.time()
    scores = get_scores(RESULTS_FILE)
    logging.info("Benchmark took %.2f seconds", end_time - start_time)

    for name, score in scores.items():
        if name != "Loop":
            report = {
                "test": f"Evolve {args.renderer} {args.trace_mode} {name} Score",
                "unit": "score",
                "score": score,
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
            }

            report_name = name.lower().replace(" ", "-")
            write_report_json(LOG_DIR, f"report-{report_name}-score.json", report)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logging.error("something went wrong running the benchmark!")
        logging.exception(ex)
        sys.exit(1)
