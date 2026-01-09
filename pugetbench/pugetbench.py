"""pugetbench for creators test script"""
import logging
import os.path
from pathlib import Path
import shutil
import sys
from argparse import ArgumentParser
import time
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
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
log_dir = script_dir / "run"
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

def safe_terminate(process_name: str):
    """Attempt to terminate a process but ignore any errors if it fails."""
    try:
        terminate_processes(process_name)
    except Exception as e:
        logging.info("Process '%s' could not be terminated (may not exist): %s", process_name, e)

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
    """Commands to initiate benchmark"""
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

        try:
            retcode = process.wait(timeout=2400)  # waits 2400 seconds = 40 minutes and if test takes longer timeout
        except TimeoutExpired as exc:
            safe_terminate(EXECUTABLE_NAME)
            raise RuntimeError("Benchmark timed out after 40 minutes. Check PugetBench logs for more info.") from exc

        stdout_thread.join()

        exc = error_in_output.get("exception")
        if exc is not None:
            raise exc

        if retcode != 0:
            safe_terminate(EXECUTABLE_NAME)
            raise RuntimeError(f"Benchmark process exited with code {retcode}")

        end_time = time.time()

        return start_time, end_time

def get_app_version_info(app: str, version_arg: str):
    """Return (full_version, trimmed_version, label) for the app."""
    config = APP_CONFIG[app]
    full_version = version_arg
    trimmed_version = trim_to_major_minor(version_arg) if version_arg else None

    if not full_version:
        full_version, trimmed_version = config["version_func"]()
        if not full_version or not trimmed_version:
            logging.error("Could not determine %s version. Is it installed?", config["label"])
            sys.exit(1)

    if config["suffix"]:
        full_version += config["suffix"]
        trimmed_version += config["suffix"]

    return full_version, trimmed_version, config["label"]

def execute_benchmark(app: str, app_version: str, benchmark_version: str):
    """Executes the benchmark and then captures the log file."""
    start_time, end_time = run_benchmark(app, app_version, benchmark_version)

    log_file = find_latest_log()

    # Check benchmark completed
    with open(log_file, encoding="utf-8") as f:
        if "Overall Score" not in f.read():
            raise RuntimeError(f"Benchmark did not complete correctly; expected 'Overall Score' not found in {log_file}")

    score = find_score_in_log(log_file)
    if score is None:
        raise RuntimeError(f"No valid score found in log: {log_file}")

    destination = Path(script_dir) / "run" / log_file.name
    shutil.copy(log_file, destination)

    return start_time, end_time, score

def main():
    """Do all the things now."""
    parser = ArgumentParser()
    parser.add_argument("--app", choices=APP_CONFIG.keys(), dest="app", help="Application name to test", required=True)
    parser.add_argument("--app_version", dest="app_version", help="Application version to test", required=False)
    parser.add_argument("--benchmark_version", dest="benchmark_version", help="PugetBench Benchmark version to use", required=False)
    args = parser.parse_args()

    full_version, trimmed_version, test_label = get_app_version_info(args.app, args.app_version)

    if args.benchmark_version is None:
        args.benchmark_version = get_latest_benchmark_by_version(args.app)

    try:
        start_time, end_time, score = execute_benchmark(
            args.app, trimmed_version, args.benchmark_version
        )

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

    except RuntimeError as e:
        msg = str(e)
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)

        # Terminate the process only for "real" failures
        if "timed out" in msg or "Benchmark failed" in msg:
            safe_terminate(EXECUTABLE_NAME)

        sys.exit(1)
    except Exception as e:
        # Non-runtime exceptions, e.g., coding errors, still exit
        logging.error("Unexpected error!")
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
