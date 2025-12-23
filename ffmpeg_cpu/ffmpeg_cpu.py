"""test script for handbrake encoding tests"""

import logging
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from time import sleep

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from ffmpeg_cpu_utils import (
    current_time_ms,
    ffmpeg_present,
    copy_ffmpeg_from_network_drive,
    is_video_source_present,
    copy_video_source
)

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    write_report_json,
)

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "harness.log"
logging.basicConfig(
    filename=LOG_FILE,
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG,
)

ENCODERS = ["h264", "av1", "h265"]
FFMPEG_EXE_PATH = SCRIPT_DIR / "ffmpeg-8.0.1-full_build" / "bin" / "ffmpeg.exe"
VMAF_VERSION = "vmaf_v0.6.1neg"
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


def check_ffmpeg_is_done():
    tl = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq ffmpeg.exe"], capture_output=True, text=True
    )
    return "ffmpeg.exe" not in tl.stdout


def main():
    """entrypoint"""
    parser = ArgumentParser()
    parser.add_argument("--encoder", dest="encoder", required=True)
    args = parser.parse_args()

    if args.encoder not in ENCODERS:
        logging.error("Invalid encoder selection: %s", args.encoder)
        sys.exit(1)
        
    if not ffmpeg_present():
        copy_ffmpeg_from_network_drive()
    
    if not is_video_source_present():
        copy_video_source()
    
    try:
        score = 0

        logging.info("starting benchmark, this may take a few minutes")
        logging.info(
            "you can ensure the test is running by checking that cpu usage is 100% in task manager"
        )
        execute_me = FFMPEG_EXE_PATH
        start_time = current_time_ms()

        if args.encoder == "h264":
            command = f"{execute_me} -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -c:v libx264 -preset slow -profile:v high -level:v 5.1 -crf 20 -c:a copy output.mp4"
        elif args.encoder == "av1":
            command = f"{execute_me} -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -c:v libsvtav1 -preset 7 -profile:v main -level:v 5.1 -crf 20 -c:a copy output.mp4"
        elif args.encoder == "h265":
            command = f"{execute_me} -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -c:v libx265 -preset slow -profile:v main -level:v 5.1 -crf 20 -c:a copy output.mp4"
        else:
            logging.error("Invalid encoder selection: %s", args.encoder)
            sys.exit(1)

        output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)

        while not check_ffmpeg_is_done():
            sleep(2)

        end_time = current_time_ms()

        logging.info("Encoding completed")
        logging.info("Beginning VMAF")

        source_path = SCRIPT_DIR / "big_buck_bunny_1080p24.y4m"
        encoded_path = SCRIPT_DIR / "output.mp4"
        filter_complex = (
            f"libvmaf=model=version={VMAF_VERSION}:n_threads=10:log_path=vmafout.txt"
        )
        argument_list = [
            "-i",
            str(source_path),
            "-i",
            str(encoded_path),
            "-filter_complex",
            filter_complex,
            "-f",
            "null",
            "-",
        ]
        logging.info("VMAF args: %s", argument_list)
        out_fp = open("output.log", "w", encoding="utf-8")
        err_fp = open("vmaf.log", "w", encoding="utf-8")
        process = subprocess.Popen(
            [FFMPEG_EXE_PATH, *argument_list], stdout=out_fp, stderr=err_fp
        )

        while not check_ffmpeg_is_done():
            sleep(2)

        logging.getLogger("").removeHandler(console)
        logging.info(output)
        logging.getLogger("").addHandler(console)

    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
