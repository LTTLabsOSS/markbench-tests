"""pugetbench for creators test script"""
import logging
import os.path
from pathlib import Path
import shutil
import sys
from argparse import ArgumentParser
import time
from subprocess import Popen, PIPE
import threading
from utils import find_latest_log, find_score_in_log, get_photoshop_version, get_premierepro_version, get_lightroom_version, get_aftereffects_version, get_davinci_version, get_pugetbench_version, get_latest_benchmark_by_version

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


def read_output(stream, log_func, error_func, error_in_output):
    """Read and log output in real-time from a stream (stdout or stderr)."""
    while True:
        line = stream.readline()
        if not line:
            break
        line = line.strip()
        log_func(line)  # Log the output

        # If line contains "Error!:", store RuntimeError to be raised later
        if line.startswith("Error!:"):
            error_func(line)
            error_in_output["exception"] = RuntimeError(
                f"Benchmark failed with error: {line}")
            break

        # If line contains "Benchmark failed:", store RuntimeError
        if line.startswith("Benchmark failed:"):
            error_in_output["exception"] = RuntimeError(
                "Benchmark had an unknown failure.")
            break

        sys.stdout.flush()  # optional here, but fine to keep


def run_benchmark(application: str, app_version: str, benchmark_version: str):
    """run benchmark"""
    start_time = time.time()
    executable_path = Path(
        f"C:\\Program Files\\PugetBench for Creators\\{EXECUTABLE_NAME}")
    command_args = ["--run_count", "1", "--rerun_count", "1",
                    "--benchmark_version", f"{benchmark_version}", "--preset",
                    "Standard", "--app_version", f"{app_version}"]
    command = None
    if application == "premierepro":
        command = [executable_path] + command_args + ["--app", "premierepro"]
    elif application == "photoshop":
        command = [executable_path] + command_args + ["--app", "photoshop"]
    elif application == "aftereffects":
        command = [executable_path] + command_args + ["--app", "aftereffects"]
    elif application == "lightroom":
        command = [executable_path] + command_args + ["--app", "lightroom"]
    elif application == "resolve":
        command = [executable_path] + command_args + ["--app", "resolve"]

    logging.info(command)

    error_in_output = {"exception": None}  # Shared state for error reporting

    with Popen(command, stdout=PIPE, stderr=PIPE, text=True) as process:
        stdout_thread = threading.Thread(target=read_output, args=(
            process.stdout, logging.info, logging.error, error_in_output))
        stderr_thread = threading.Thread(target=read_output, args=(
            process.stderr, logging.error, logging.error, error_in_output))

        stdout_thread.start()
        stderr_thread.start()

        process.wait()

        stdout_thread.join()
        stderr_thread.join()

        # Raise the error if detected before exiting the block
        if error_in_output["exception"]:
            raise RuntimeError(error_in_output["exception"])

    end_time = time.time()

    return start_time, end_time


def main():
    """main"""

    start_time = time.time()
    parser = ArgumentParser()
    parser.add_argument("--app", dest="app",
                        help="Application name to test", required=True)
    parser.add_argument(
        "--app_version", dest="app_version",
        help="Application version to test", required=False)
    parser.add_argument(
        "--benchmark_version", dest="benchmark_version",
        help="Puget Bench Benchmark version to use", required=False)
    args = parser.parse_args()
    apps = [
        "premierepro",
        "photoshop",
        "aftereffects",
        "lightroom",
        "resolve"
    ]

    if args.app is None or args.app not in apps:
        logging.info("unrecognized option for program")
        sys.exit(1)

    if args.benchmark_version is None:
        args.benchmark_version = get_latest_benchmark_by_version(args.app)

    version = args.app_version
    score = 0
    full_version = None
    trimmed_version = None
    test = ""
    if args.app == "premierepro":
        test = "Adobe Premiere Pro"
        if version is None:
            full_version, trimmed_version = get_premierepro_version()
    elif args.app == "photoshop":
        test = "Adobe Photoshop"
        if version is None:
            full_version, trimmed_version = get_photoshop_version()
    elif args.app == "aftereffects":
        test = "Adobe After Effects"
        if version is None:
            full_version, trimmed_version = get_aftereffects_version()
    elif args.app == "lightroom":
        test = "Adobe Lightroom Classic"
        if version is None:
            full_version, trimmed_version = get_lightroom_version()
    elif args.app == "resolve":
        test = "Davinci Resolve Studio"
        if version is None:
            full_version, trimmed_version = get_davinci_version()
            if full_version and trimmed_version:
                full_version += "-studio"
                trimmed_version += "-studio"

    try:
        start_time, end_time = run_benchmark(
            args.app, trimmed_version, args.benchmark_version)
        log_file = find_latest_log()
        score = find_score_in_log(log_file)
        destination = Path(script_dir) / "run" / os.path.split(log_file)[1]
        shutil.copy(log_file, destination)

        report = {
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
            "test": "PugetBench",
            "test_parameter": test,
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
