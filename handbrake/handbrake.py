"""test script for handbrake encoding tests"""
from argparse import ArgumentParser
import os
import re
from handbrake_utils import HANDBRAKE_EXECUTABLE, current_time_ms, handbrake_present, is_video_source_present, copy_video_source, copy_handbrake_from_network_drive
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    write_report_json
)

ENCODER_TO_PRESET = {
        "h264": {
            "file": "./presets/h264_bigbuckbunny_1080p_cpu_test.json",
            "name": "CPU 1080p BBB H264"
        },
        "h265": {
            "file": "./presets/h265_bigbuckbunny_1080p_cpu_test.json",
            "name": "CPU 1080p BBB H265"
        },
        "av1": {
            "file": "./presets/av1-svt_bigbuckbunny_1080p_cpu_test.json",
            "name": "CPU 1080p BBB AV1"
        }
    }

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "harness.log"
logging.basicConfig(
    filename=LOG_FILE,
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG
)

console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

def main():
    """entrypoint"""
    parser = ArgumentParser()
    parser.add_argument("-e", "--encoder", dest="encoder",
                        help="encoder", metavar="encoder", required=True)
    args = parser.parse_args()

    if args.encoder not in list(ENCODER_TO_PRESET.keys()):
        logging.error(f"Invalid encoder selection: {args.encoder}")
        sys.exit(1)

    try:
        score = 0
        preset = ENCODER_TO_PRESET[args.encoder]
        if handbrake_present() is False:
            logging.info("copying handbrake from network drive")
            copy_handbrake_from_network_drive()
        else:
            logging.info("detected handbrake")

        if is_video_source_present() is False:
            logging.info("copying big buck bunny from network drive")
            copy_video_source()
        else:
            logging.info("detected big buck bunny source file")

        logging.info("starting benchmark, this may take a few minutes")
        logging.info(
            "you can ensure the test is running by checking that cpu usage is 100% in task manager")
        command = f"{SCRIPT_DIR}\\{HANDBRAKE_EXECUTABLE}"
        start_time = current_time_ms()
        avgencoding_pattern = r'average encoding speed for job is (\d+\.\d+) fps'
        output = subprocess.check_output([
            command,
            "-i",
            "big_buck_bunny_1080p24.y4m",
            "-o",
            "bbboutput.mp4",
            "--preset-import-file",
            preset['file'],
            "--preset",
            preset['name']],
            text=True,
            stderr=subprocess.STDOUT)
        end_time = current_time_ms()

        logging.getLogger("").removeHandler(console)
        logging.info(output)
        logging.getLogger("").addHandler(console)
       
        match = re.search(avgencoding_pattern, output)
        if not match:
            raise Exception("score was not found in the process output!")
        score = match.group(1)
        logging.info(f"Average Encoding Speed: {score}")
        logging.info(f"Finished in: {(end_time - start_time) / 1000} seconds")

        end_time = current_time_ms()

        report = {
            "test": f"HandBrake Encoding BBB {args.encoder.upper()}",
            "score": score,
            "unit": "frames per second",
            "version": "1.8.1",
            "start_time": start_time,
            "end_time": end_time
        }

        write_report_json(LOG_DIR, "report.json", report)
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
