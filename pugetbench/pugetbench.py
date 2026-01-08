"""pugetbench for creators test script"""
import logging
import os.path
from pathlib import Path
import shutil
import sys
from argparse import ArgumentParser
import time
from subprocess import Popen, PIPE, STDOUT
import threading
from utils import find_latest_log, trim_to_major_minor, find_score_in_log, get_photoshop_version, get_premierepro_version, get_lightroom_version, get_aftereffects_version, get_davinci_version, get_pugetbench_version, get_latest_benchmark_by_version

sys.path.insert(1, os.path.join(sys.path[0], ".."))
from harness_utils.process import terminate_processes
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT
)

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
setup_log_directory(log_dir)
logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

EXECUTABLE_NAME = "PugetBench for Creators.exe"

APP_CONFIG = {
    "premierepro": {
        "label": "Adobe Premiere Pro",
        "version_func": get_premierepro_version,
        "suffix": None,
    },
    "photoshop": {
        "label": "Adobe Photoshop",
        "version_func": get_photoshop_version,
        "suffix": None,
    },
    "aftereffects": {
        "label": "Adobe After Effects",
        "version_func": get_aftereffects_version,
        "suffix": None,
    },
    "lightroom": {
        "label": "Adobe Lightroom Classic",
        "version_func": get_lightroom_version,
        "suffix": None,
    },
    "resolve": {
        "label": "Davinci Resolve Studio",
        "version_func": get_davinci_version,
        "suffix": "-studio",
    },
}

def read_output(stream, log_func, error_func, error_in_output):
    """Read and log output in real-time from a stream (stdout or stderr)."""
    for line in iter(stream.readline, ''):
        line = line.strip()
        log_func(line)
        # If getting a known error
        if line.startswith("Error!:"):
            error_func(line)
            error_in_output["exception"] = RuntimeError(f"Benchmark failed with error: {line}")
            break
        # If getting a benchmark unknown failure
        if line.startswith("Benchmark failed:"):
            error_in_output["exception"] = RuntimeError("Benchmark had an unknown failure.")
            break
        # NEW: catch unsupported version / benchmark mismatch
        if "not supported" in line:
            error_func(line)
            error_in_output["exception"] = RuntimeError(f"Benchmark version mismatch: {line}")
            break
        sys.stdout.flush()


def run_benchmark(application: str, app_version: str, benchmark_version: str):
    """run benchmark"""
    start_time = time.time()
    executable_path = Path(f"C:\\Program Files\\PugetBench for Creators\\{EXECUTABLE_NAME}")
    if not executable_path.exists():
        logging.error("PugetBench executable not found at %s", executable_path)
        sys.exit(1)

    command = [
        executable_path,
        "--run_count", "1",
        "--rerun_count", "1",
        "--benchmark_version", benchmark_version,
        "--preset", "Standard",
        "--app_version", app_version,
        "--app", application
    ]

    logging.info("Running benchmark command: %s", command)

    logging.info(command)

    error_in_output = {"exception": None}  # Shared state for error reporting

    with Popen(command, stdout=PIPE, stderr=STDOUT, text=True, bufsize=1) as process:
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, logging.info, logging.error, error_in_output))
        stdout_thread.start()

        retcode = process.wait()
        stdout_thread.join()

        if error_in_output["exception"]:
            raise error_in_output["exception"]

        if retcode != 0:
            raise RuntimeError(f"Benchmark process exited with code {retcode}")

        end_time = time.time()

        return start_time, end_time


def main():
    """main"""

    start_time = time.time()
    parser = ArgumentParser()
    parser.add_argument("--app", choices=APP_CONFIG.keys(), dest="app", help="Application name to test", required=True)
    parser.add_argument("--app_version", dest="app_version",help="Application version to test", required=False)
    parser.add_argument("--benchmark_version", dest="benchmark_version", help="Puget Bench Benchmark version to use", required=False)
    args = parser.parse_args()

    config = APP_CONFIG[args.app]
    test_label = config["label"]

    # if args.app is None or args.app not in apps:
    #     logging.info("unrecognized option for program")
    #     sys.exit(1)

    # Determine app version
    if args.app_version is None:
        full_version, trimmed_version = config["version_func"]()
        if not full_version or not trimmed_version:
            logging.error("Could not determine %s version. Is it installed?", test_label)
            sys.exit(1)
    else:
        full_version = args.app_version
        trimmed_version = trim_to_major_minor(full_version)

    # Apply optional suffix (e.g., Resolve)
    if config["suffix"]:
        full_version += config["suffix"]
        trimmed_version += config["suffix"]

    if args.benchmark_version is None:
        args.benchmark_version = get_latest_benchmark_by_version(args.app)

    try:
        start_time, end_time = run_benchmark(args.app, trimmed_version, args.benchmark_version)

        log_file = find_latest_log()
        # Check that the benchmark actually wrote expected output
        with open(log_file, encoding="utf-8") as f:
            log_content = f.read()
        expected_marker = "Overall Score"
        if expected_marker not in log_content:
            raise RuntimeError(f"Benchmark did not complete correctly; expected '{expected_marker}' not found in log {log_file}")

        # Grab the score
        score = find_score_in_log(log_file)
        if score is None:
            raise RuntimeError(f"No valid score found in log: {log_file}")

        # Copy the log
        destination = Path(script_dir) / "run" / log_file.name
        shutil.copy(log_file, destination)

        report = {
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
            "test": "PugetBench",
            "test_parameter": test_label,
            "app_version": full_version,
            "benchmark_version": args.benchmark_version,
            "pugetbench_version": get_pugetbench_version(),
            "unit": "Score",
            "score": score
        }

        write_report_json(log_dir, "report.json", report)

    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        terminate_processes(EXECUTABLE_NAME)
        sys.exit(1)


if __name__ == "__main__":
    main()
