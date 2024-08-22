"""godot compile test script"""
import logging
import os
import sys
import re
from pathlib import Path
from subprocess import Popen
from godot_compile_utils import  convert_duration_string_to_seconds, copy_godot_source_from_network_drive, create_conda_environment, install_mingw, install_miniconda, run_conda_command

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from handbrake.handbrake_utils import current_time_ms
from harness_utils.output import write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")

def setup_logging():
    """Configures root logger"""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(filename=f'{LOG_DIR}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def main():
    """test script entry point"""
    setup_logging()
    output = install_mingw()
    logging.info(output)

    output = install_miniconda()
    logging.info(output)

    output = copy_godot_source_from_network_drive()
    logging.info(output)

    output = create_conda_environment()
    logging.info(output)

    output = run_conda_command(["pip", "install", "scons"])
    logging.info(output)

    output = run_conda_command([
        "scons",
        "--clean",
        "--no-cache",
        "platform=windows",
        "arch=x86_64"
    ])
    logging.info(output)

    start_time = current_time_ms()
    output = run_conda_command([
        "scons",
        "--no-cache",
        "platform=windows",
        "arch=x86_64"
    ])
    logging.info(output)
    end_time = current_time_ms()

    score_regex = r'Time elapsed: (\d\d:\d\d:\d\d\.\d+)'
    score = None
    for line in output.splitlines():
        score_match = re.search(score_regex, line.strip())
        if score_match: 
            duration_string  = score_match.group(1)
            score = convert_duration_string_to_seconds(duration_string)
            break

    if score is None: 
            raise Exception("could not find score from scons output, check log and try again")
    
    report = {
        "start_time": start_time,
        "version": "4.2.1-stable",
        "end_time": end_time,
        "score": score,
        "unit": "seconds",
        "test": "Godot 4.2.1 Compile"
    }

    write_report_json(LOG_DIR, "report.json", report)

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logging.error("error running benchmark")
        logging.error(ex)
        sys.exit(1)
