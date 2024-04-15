"""pugetbench for creators test script"""
import json
import logging
import os.path
from pathlib import Path
import shutil
import sys
from argparse import ArgumentParser
import time
from subprocess import Popen
from utils import find_latest_log, find_score_in_log

sys.path.insert(1, os.path.join(sys.path[0], ".."))
from harness_utils.process import terminate_processes
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
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

executable_name = "PugetBench for Creators.exe"

def run_benchmark(application: str) -> Popen:
    start_time = time.time()
    executable_path =  Path(f"C:\\Program Files\\PugetBench for Creators\\{executable_name}")
    command_args = ["--run_count" , "1", "--rerun_count", "1", "--benchmark_version", "1.0.0", "--preset", "Standard"]
    photoshop_args = command_args + ["--app", "photoshop"]
    premiere_args = command_args + ["--app", '"Premiere Pro"']

    process = None
    if application == "premiere":
        process = Popen([executable_path] +  premiere_args)
    elif application == "photoshop":
        process = Popen([executable_path] + photoshop_args)
    
    exit_code = process.wait()
    end_time = time.time()
    return start_time, end_time, exit_code

def main():
    start_time = time.time()
    parser = ArgumentParser()
    parser.add_argument(
        "--app", dest="app", help="Host for Keras OCR service", required=True
    )
    args = parser.parse_args()
    apps = [
        "premiere",
        "photoshop"
    ]

    if args.app is None or args.app not in apps:
        logging.info(f"unrecognized option for program {args.app}")
        print('what')
        sys.exit(1)

    # 1 check if pugetbench is installed
    # 2 check adobe photoshop or premiere is present
    # parse the report
    # print the report

    score = 0
    test = ""
    if args.app == "premiere":
        test = "Adobe Premiere Pro"
    elif args.app == "photoshop":
        test = "Adobe Photoshop"

    try:
        start_time, end_time, exit_code = run_benchmark(args.app)

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
        terminate_processes(executable_name)
        sys.exit(1)


if __name__ == "__main__":
    main()
