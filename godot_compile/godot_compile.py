"""godot compile test script"""

import logging
import re
import sys
from pathlib import Path

from godot_compile_utils import (
    convert_duration_string_to_seconds,
    copy_godot_source_from_network_drive,
    create_conda_environment,
    install_mingw,
    install_miniconda,
    run_conda_command,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from godot_compile_utils import current_time_ms

from harness_utils.output import setup_logging, write_report_json

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"


def main():
    """test script entry point"""
    setup_logging(LOG_DIRECTORY)
    output = install_mingw()
    logging.info(output)

    output = install_miniconda()
    logging.info(output)

    output = copy_godot_source_from_network_drive()
    logging.info(output)

    output = create_conda_environment()
    logging.info(output)

    output = run_conda_command(["python", "-m", "pip", "install", "scons"])
    logging.info(output)

    output = run_conda_command(
        ["scons", "--clean", "--no-cache", "platform=windows", "arch=x86_64"]
    )
    logging.info(output)

    start_time = current_time_ms()
    output = run_conda_command(
        ["scons", "--no-cache", "platform=windows", "arch=x86_64"]
    )
    logging.info(output)
    end_time = current_time_ms()

    score_regex = r"Time elapsed: (\d\d:\d\d:\d\d\.\d+)"
    score = None
    for line in output.splitlines():
        score_match = re.search(score_regex, line.strip())
        if score_match:
            duration_string = score_match.group(1)
            score = convert_duration_string_to_seconds(duration_string)
            break

    if score is None:
        raise Exception(
            "could not find score from scons output, check log and try again"
        )

    report = {
        "start_time": start_time,
        "version": "4.4.1-stable",
        "end_time": end_time,
        "score": score,
        "unit": "seconds",
        "test": "Godot 4.4.1 Compile",
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logging.error("error running benchmark")
        logging.exception(ex)
        sys.exit(1)
