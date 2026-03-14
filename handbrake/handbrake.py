"""test script for handbrake encoding tests"""
from argparse import ArgumentParser
import os
import re
from handbrake_utils import HANDBRAKE_EXECUTABLE, current_time_ms, handbrake_present, is_video_source_present, copy_video_source, copy_handbrake_from_network_drive
import logging
import subprocess
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import (
    setup_logging,
    write_report_json)


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)

ENCODER_TO_PRESET = {
    "h264_cpu": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\h264_bigbuckbunny_1080p_cpu_test.json",
        "name": "\"CPU 1080p BBB H264\"",
        "api": "cpu"
    },
    "h265_cpu": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\h265_bigbuckbunny_1080p_cpu_test.json",
        "name": "\"CPU 1080p BBB H265\"",
        "api": "cpu"
    },
    "av1_cpu": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\av1-svt_bigbuckbunny_1080p_cpu_test.json",
        "name": "\"CPU 1080p BBB AV1\"",
        "api": "cpu"
    },
    "h264_nvenc": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\h264_nvenc_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"NVENC 1080p BBB H264\"",
        "api": "nvenc"
    },
    "h265_nvenc": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\h265_nvenc_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"NVENC 1080p BBB H265\"",
        "api": "nvenc"
    },
    "av1_nvenc": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\av1-nvenc_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"NVENC 1080p BBB AV1\"",
        "api": "nvenc"
    },
    "h264_vce": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\h264-vce-bigbuckbunny_1080p_gpu_test.json",
        "name": "\"AMD VCE 1080p BBB H264\"",
        "api": "vce"
    },
    "av1_vce": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\av1-vce-bigbuckbunny_1080p_gpu_test.json",
        "name": "\"AMD VCE 1080p BBB AV1\"",
        "api": "vce"
    },
    "h264_quicksync": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\h264-quicksync_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"QUICKSYNC 1080p BBB H264\"",
        "api": "quicksync"
    },
    "av1_quicksync": {
        "file": f"{SCRIPT_DIRECTORY}\\presets\\av1-quicksync_bigbuckbunny_1080p_gpu_test.json",
        "name": "\"QUICKSYNC 1080p BBB AV1\"",
        "api": "quicksync"
    }
}


def main():
    """entrypoint"""
    parser = ArgumentParser()
    parser.add_argument("-e", "--encoder", dest="encoder",
                        help="encoder", metavar="encoder", required=True)
    args = parser.parse_args()

    if args.encoder not in ENCODER_TO_PRESET:
        logging.error("Invalid encoder selection: %s", args.encoder)
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
        execute_me = f"{SCRIPT_DIRECTORY}\\{HANDBRAKE_EXECUTABLE}"
        start_time = current_time_ms()
        avgencoding_pattern = r'average encoding speed for job is (\d+\.\d+) fps'
        command = f"{execute_me} -i {SCRIPT_DIRECTORY}\\big_buck_bunny_1080p24.y4m -o {SCRIPT_DIRECTORY}\\bbboutput.mp4 --preset-import-file {preset['file']} --preset {preset['name']}"

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

        write_report_json(LOG_DIRECTORY, "report.json", report)
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
