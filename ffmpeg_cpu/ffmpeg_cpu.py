"""test script for handbrake encoding tests"""

import logging
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

from harness_utils.artifacts import ArtifactManager, ArtifactType

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from ffmpeg_cpu_utils import (
    copy_ffmpeg_from_network_drive,
    copy_video_source,
    current_time_ms,
    ffmpeg_present,
    is_video_source_present,
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
FFMPEG_VERSION = "ffmpeg-8.0.1-full_build"
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
        start_encoding_time = current_time_ms()
        logging.info("Starting ffmpeg_cpu benchmark...")

        if args.encoder == "h264":
            command = f"{FFMPEG_EXE_PATH} -y -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -c:v libx264 -preset slow -profile:v high -level:v 5.1 -crf 20 -c:a copy output.mp4"
        elif args.encoder == "av1":
            command = f"{FFMPEG_EXE_PATH} -y -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -c:v libsvtav1 -preset 7 -profile:v main -level:v 5.1 -crf 20 -c:a copy output.mp4"
        elif args.encoder == "h265":
            command = f"{FFMPEG_EXE_PATH} -y -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -c:v libx265 -preset slow -profile:v main -level:v 5.1 -crf 20 -c:a copy output.mp4"
        else:
            logging.error("Invalid encoder selection: %s", args.encoder)
            sys.exit(1)

        logging.info("Executing command: %s", command)

        with open("encoding.log", "w", encoding="utf-8") as encoding_log:
            logging.info("Encoding...")
            subprocess.run(command, stderr=encoding_log, check=True)

        end_encoding_time = current_time_ms()
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

        vmaf_score = None
        with open("vmaf.log", "w+", encoding="utf-8") as vmaf_log:
            logging.info("Calculating VMAF...")
            subprocess.run(
                [FFMPEG_EXE_PATH, *argument_list], stderr=vmaf_log, check=True
            )
            vmaf_log.flush()
            vmaf_log.seek(0)
            for line in reversed(vmaf_log.read().splitlines()):
                if "VMAF score:" in line:
                    match = re.search(r"VMAF score:\s*([0-9]+(?:\.[0-9]+)?)", line)
                    if match:
                        vmaf_score = float(match.group(1))
                    break
        end_time = current_time_ms()
        logging.info("VMAF score: %s", vmaf_score)

        logging.getLogger("").removeHandler(console)
        logging.getLogger("").addHandler(console)

        am = ArtifactManager(LOG_DIR)
        am.copy_file("ffmpeg.log", ArtifactType.RESULTS_TEXT, "ffmpeg log file")
        am.copy_file("vmaf.log", ArtifactType.RESULTS_TEXT, "vmaf log file")
        am.create_manifest()

        report = {
            "test": "FFMPEG CPU Encoding",
            "test_parameter": str(args.encoder),
            "ffmpeg_version": FFMPEG_VERSION,
            "vmaf_version": VMAF_VERSION,
            "score": vmaf_score,
            "unit": "score",
            "encoding_duration": end_encoding_time - start_encoding_time,
            "vmaf_duration": end_time - end_encoding_time,
            "start_time": start_encoding_time,
            "end_time": end_time,
        }
        write_report_json(str(LOG_DIR), "report.json", report)
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
