"""Test script for FFmpeg encoding tests."""

import logging
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from ffmpeg_cpu_utils import (
    copy_vmaf,
    copy_video_source,
    current_time_ms,
    get_ffmpeg,
    get_ffmpeg_root,
    vmaf_supported,
)
from harness_utils.artifacts import create_artifacts_manifest
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.report import write_report_json


logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)

setup_logging(LOG_DIRECTORY)

ENCODERS = [
    "h264",
    "av1",
    "h265",
]

ARCHITECTURES = [
    "x86_64",
    "arm64",
]

VMAF_VERSION = "vmaf_v0.6.1neg"

INPUT_VIDEO = SCRIPT_DIRECTORY / "big_buck_bunny_1080p24.y4m"
OUTPUT_VIDEO = SCRIPT_DIRECTORY / "output.mp4"


def build_encoder_command(encoder, ffmpeg_exe_path):
    """Build the FFmpeg encoding command for the selected encoder."""
    common_arguments = [
        ffmpeg_exe_path,
        "-y",
        "-i",
        INPUT_VIDEO,
    ]

    if encoder == "h264":
        return [
            *common_arguments,
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-profile:v",
            "high",
            "-level:v",
            "5.1",
            "-crf",
            "20",
            "-c:a",
            "copy",
            OUTPUT_VIDEO,
        ]

    if encoder == "av1":
        return [
            *common_arguments,
            "-c:v",
            "libsvtav1",
            "-preset",
            "7",
            "-profile:v",
            "main",
            "-level:v",
            "5.1",
            "-crf",
            "20",
            "-c:a",
            "copy",
            OUTPUT_VIDEO,
        ]

    if encoder == "h265":
        return [
            *common_arguments,
            "-c:v",
            "libx265",
            "-preset",
            "slow",
            "-profile:v",
            "main",
            "-level:v",
            "5.1",
            "-crf",
            "20",
            "-c:a",
            "copy",
            OUTPUT_VIDEO,
        ]

    raise ValueError(f"Unsupported encoder: {encoder}")


def parse_encoding_results(encoding_log_path):
    """Parse encoding FPS and duration from the FFmpeg log."""
    encoding_fps = None
    encoding_duration_seconds = None

    with open(
        encoding_log_path,
        "r",
        encoding="utf-8",
    ) as encoding_log:
        lines = encoding_log.read().splitlines()

    for line in reversed(lines):
        line = line.strip()

        frame_match = re.search(
            r"frame=\s?(\d+)\s"
            r"fps=\s?([0-9]+(?:\.[0-9]+)?)"
            r".*elapsed=\s?(\d+:\d{2}:\d{2}\.\d+)",
            line,
        )

        if not frame_match:
            continue

        encoding_fps = float(frame_match.group(2))

        hours, minutes, seconds = frame_match.group(3).split(":")

        encoding_duration_seconds = (
            int(hours) * 3600
            + int(minutes) * 60
            + float(seconds)
        )

        break

    if encoding_fps is None:
        raise RuntimeError(
            "Failed to parse encoding FPS from FFmpeg output"
        )

    return encoding_fps, encoding_duration_seconds


def run_encoding(ffmpeg_exe_path, encoder):
    """Run the FFmpeg encoding benchmark."""
    command = build_encoder_command(
        encoder,
        ffmpeg_exe_path,
    )

    logger.info("Executing command: %s", command)

    encoding_log_path = ARTIFACTS_DIRECTORY / "encoding.log"

    with open(
        encoding_log_path,
        "w",
        encoding="utf-8",
    ) as encoding_log:
        logger.info("Encoding...")

        subprocess.run(
            command,
            stderr=encoding_log,
            check=True,
        )

    logger.info("Encoding completed")

    return parse_encoding_results(
        encoding_log_path
    )


def run_vmaf(ffmpeg_exe_path, architecture):
    """Run the VMAF quality measurement."""
    if not vmaf_supported(architecture):
        logger.info(
            "VMAF not supported in this FFmpeg build"
        )
        return None, None

    logger.info("Beginning VMAF")

    start_vmaf_time = current_time_ms()

    vmaf_model_path = (
        get_ffmpeg_root(architecture)
        / "vmaf"
        / f"{VMAF_VERSION}.json"
    )

    filter_complex = (
        f"libvmaf="
        f"model=path={vmaf_model_path}"
        f":n_threads=10"
        f":log_path=vmafout.txt"
    )

    argument_list = [
        "-i",
        INPUT_VIDEO,
        "-i",
        OUTPUT_VIDEO,
        "-filter_complex",
        filter_complex,
        "-f",
        "null",
        "-",
    ]

    logger.info("VMAF args: %s", argument_list)

    vmaf_log_path = ARTIFACTS_DIRECTORY / "vmaf.log"

    with open(
        vmaf_log_path,
        "w+",
        encoding="utf-8",
    ) as vmaf_log:
        logger.info("Calculating VMAF...")

        subprocess.run(
            [
                ffmpeg_exe_path,
                *argument_list,
            ],
            cwd=ffmpeg_exe_path.parent,
            stderr=vmaf_log,
            check=True,
        )

        vmaf_log.flush()
        vmaf_log.seek(0)

        for line in reversed(vmaf_log.read().splitlines()):
            if "VMAF score:" not in line:
                continue

            match = re.search(
                r"VMAF score:\s*"
                r"([0-9]+(?:\.[0-9]+)?)",
                line,
            )

            if match:
                vmaf_score = float(match.group(1))
            else:
                vmaf_score = None

            break
        else:
            vmaf_score = None

    vmaf_duration = current_time_ms() - start_vmaf_time

    logger.info(
        "VMAF score: %s",
        vmaf_score,
    )

    return vmaf_score, vmaf_duration


def main():
    """Run the FFmpeg CPU benchmark."""
    parser = ArgumentParser()

    parser.add_argument(
        "--encoder",
        dest="encoder",
        required=True,
        choices=ENCODERS,
    )

    parser.add_argument(
        "-a",
        "--architecture",
        dest="architecture",
        help="Architecture type",
        required=True,
        choices=ARCHITECTURES,
    )

    args = parser.parse_args()

    try:
        ffmpeg_exe_path, ffmpeg_version = get_ffmpeg(
            args.architecture
        )

        logger.info(
            "Using FFmpeg %s: %s",
            ffmpeg_version,
            ffmpeg_exe_path,
        )

        copy_vmaf(args.architecture)

        if not INPUT_VIDEO.is_file():
            logger.info(
                "Video source not found, copying from network drive..."
            )
            copy_video_source()

        start_encoding_time = current_time_ms()

        logger.info(
            "Starting ffmpeg_cpu benchmark..."
        )

        encoding_fps, encoding_duration = run_encoding(
            ffmpeg_exe_path,
            args.encoder,
        )

        logger.info(
            "Encoding FPS (overall): %s",
            encoding_fps,
        )

        vmaf_score, vmaf_duration = run_vmaf(
            ffmpeg_exe_path,
            args.architecture,
        )

        end_time = current_time_ms()

        report = {
            "test": "FFMPEG CPU Encoding",
            "test_parameter": args.encoder,
            "architecture": args.architecture,
            "ffmpeg_version": ffmpeg_version,
            "score": encoding_fps,
            "unit": "frames per second",
            "encoding_duration": encoding_duration,
            "start_time": start_encoding_time,
            "end_time": end_time,
        }

        if vmaf_score is not None:
            report.update(
                {
                    "vmaf_version": VMAF_VERSION,
                    "vmaf_score": vmaf_score,
                    "vmaf_duration": vmaf_duration,
                }
            )

        write_report_json(
            LOG_DIRECTORY,
            "report.json",
            report,
        )

        create_artifacts_manifest(
            ARTIFACTS_DIRECTORY
        )

    except Exception:
        logger.error(
            "Something went wrong running the benchmark!"
        )
        logger.exception(
            "Unhandled exception"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()