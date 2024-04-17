"""pugetbench for creators test script"""
import logging
import os.path
from pathlib import Path
import shutil
import sys
from argparse import ArgumentParser
import time
from subprocess import Popen
from utils import find_latest_log, find_score_in_log, get_photoshop_version, get_premierepro_version

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

def run_benchmark(application: str, app_version: str) -> Popen:
    """run benchmark"""
    start_time = time.time()
    executable_path =  Path(f"C:\\Program Files\\PugetBench for Creators\\{EXECUTABLE_NAME}")
    command_args = ["--run_count" , "1", "--rerun_count", "1", "--benchmark_version", "1.0.0", "--preset", "Standard", "--app_version", f"{app_version}"]
    photoshop_args = command_args + ["--app", "photoshop"]
    premiere_args = command_args + ["--app", "premierepro"]
    command = None
    if application == "premierepro":
        command = [executable_path] +  premiere_args
    elif application == "photoshop":
        command =[executable_path] + photoshop_args

    with Popen(command) as process:
        exit_code = process.wait()
        end_time = time.time()
        return start_time, end_time, exit_code

def main():
    """main"""
    start_time = time.time()
    parser = ArgumentParser()
    parser.add_argument(
        "--app", dest="app", help="Application name to test", required=True
    )
    parser.add_argument(
        "--app_version", dest="app_version", help="Application version to test", required=False
    )
    args = parser.parse_args()
    apps = [
        "premierepro",
        "photoshop"
    ]

    if args.app is None or args.app not in apps:
        logging.info("unrecognized option for program")
        sys.exit(1)

    version = args.app_version
    score = 0
    test = ""
    if args.app == "premierepro":
        test = "PugetBench Adobe Premiere Pro"
        if version is None:
            version = get_premierepro_version()
    elif args.app == "photoshop":
        test = "PugentBench Adobe Photoshop"
        if version is None:
            version = get_photoshop_version()

    try:
        start_time, end_time, exit_code = run_benchmark(args.app, version)

        if exit_code > 0:
            logging.error("Test failed!")
            sys.exit(exit_code)
        log_file = find_latest_log()
        score = find_score_in_log(log_file)
        destination = Path(script_dir) / "run" / os.path.split(log_file)[1]
        shutil.copy(log_file, destination)

        report = {
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
            "test": test,
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
