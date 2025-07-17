"""test script for handbrake encoding tests"""
from argparse import ArgumentParser
import os
import re
from handbrake_utils import (
    HANDBRAKE_EXECUTABLE,
    current_time_ms,
    handbrake_present,
    is_video_source_present,
    copy_video_source,
    copy_handbrake_from_network_drive,
    connect_and_copy_handbrake,
    connect_and_copy_video
)
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

ENCODER_TO_PRESET = {
    "h264_cpu": {
        "file": f"{SCRIPT_DIR}\\presets\\h264_bigbuckbunny_1080p_cpu_test.json",
        "name": "\"CPU 1080p BBB H264\"",
        "api": "cpu"
    },
    "h265_cpu": {
        "file": f"{SCRIPT_DIR}\\presets\\h265_bigbuckbunny_1080p_cpu_test.json",
        "name": "\"CPU 1080p BBB H265\"",
        "api": "cpu"
    },
    "av1_cpu": {
        "file": f"{SCRIPT_DIR}\\presets\\av1-svt_bigbuckbunny_1080p_cpu_test.json",
        "name": "\"CPU 1080p BBB AV1\"",
        "api": "cpu"
    },
    "h264_nvenc": {
        "file": f"{SCRIPT_DIR}\\presets\\h264_nvenc_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"NVENC 1080p BBB H264\"",
        "api": "nvenc"
    },
    "h265_nvenc": {
        "file": f"{SCRIPT_DIR}\\presets\\h265_nvenc_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"NVENC 1080p BBB H265\"",
        "api": "nvenc"
    },
    "av1_nvenc": {
        "file": f"{SCRIPT_DIR}\\presets\\av1-nvenc_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"NVENC 1080p BBB AV1\"",
        "api": "nvenc"
    },
    "h264_vce": {
        "file": f"{SCRIPT_DIR}\\presets\\h264-vce-bigbuckbunny_1080p_gpu_test.json",
        "name": "\"AMD VCE 1080p BBB H264\"",
        "api": "vce"
    },
    "av1_vce": {
        "file": f"{SCRIPT_DIR}\\presets\\av1-vce-bigbuckbunny_1080p_gpu_test.json",
        "name": "\"AMD VCE 1080p BBB AV1\"",
        "api": "vce"
    },
    "h264_quicksync": {
        "file": f"{SCRIPT_DIR}\\presets\\h264-quicksync_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"QUICKSYNC 1080p BBB H264\"",
        "api": "quicksync"
    },
    "av1_quicksync": {
        "file": f"{SCRIPT_DIR}\\presets\\av1-quicksync_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"QUICKSYNC 1080p BBB AV1\"",
        "api": "quicksync"
    }
}


console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


def main():
    """entrypoint"""
    parser = ArgumentParser()
    parser.add_argument("-e", "--encoder", dest="encoder",
                        help="encoder", metavar="encoder", required=True)
    parser.add_argument("--shareUser", dest="share_user", required=False, default=None)
    parser.add_argument("--sharePass", dest="share_pass", required=False, default=None)
    args = parser.parse_args()

    if args.encoder not in ENCODER_TO_PRESET:
        logging.error("Invalid encoder selection: %s", args.encoder)
        sys.exit(1)

    try:
        score = 0
        preset = ENCODER_TO_PRESET[args.encoder]
        if handbrake_present() is False:
            logging.info("copying handbrake from network drive")
            if args.share_user is not None and args.share_pass is not None:
                connect_and_copy_handbrake(args.share_user, args.share_pass)
            else:
                copy_handbrake_from_network_drive()

        else:
            logging.info("detected handbrake")

        if is_video_source_present() is False:
            logging.info("copying big buck bunny from network drive")
            if args.share_user is not None and args.share_pass is not None:
                connect_and_copy_video(args.share_user, args.share_pass)
            else:
                copy_video_source()

        else:
            logging.info("detected big buck bunny source file")

        logging.info("starting benchmark, this may take a few minutes")
        logging.info(
            "you can ensure the test is running by checking that cpu usage is 100% in task manager")
        execute_me = f"{SCRIPT_DIR}\\{HANDBRAKE_EXECUTABLE}"
        start_time = current_time_ms()
        avgencoding_pattern = r'average encoding speed for job is (\d+\.\d+) fps'
        command = f"{execute_me} -i {SCRIPT_DIR}\\big_buck_bunny_1080p24.y4m -o {SCRIPT_DIR}\\bbboutput.mp4 --preset-import-file {preset['file']} --preset {preset['name']}"

        output = subprocess.check_output(
            command,
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
        logging.info("Average Encoding Speed: %s", score)
        duration = (end_time - start_time) / 1000
        logging.info("Finished in: %f seconds", duration)

        end_time = current_time_ms()

        report = {
            "test": "HandBrake Encoding",
            "test_parameter": f"{ENCODER_TO_PRESET[args.encoder]['name']}",
            "api": ENCODER_TO_PRESET[args.encoder]['api'],
            "score": score,
            "unit": "frames per second",
            "version": "1.9.1",
            "start_time": start_time,
            "end_time": end_time
        }

        write_report_json(str(LOG_DIR), "report.json", report)
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
