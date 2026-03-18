"""Blender render test script"""

import logging
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from blender_utils import (
    BENCHMARK_CONFIG,
    download_scene,
    find_blender,
    run_blender_render,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"


VALID_DEVICES = ["CPU", "CUDA", "OPTIX", "HIP", "ONEAPI", "METAL"]


def main():
    """entry point for test script"""
    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--device", dest="device", help="device", metavar="device", required=True
    )
    parser.add_argument(
        "--benchmark",
        dest="benchmark",
        help="Benchmark test type",
        metavar="benchmark",
        required=True,
    )
    args = parser.parse_args()
    if args.device not in VALID_DEVICES:
        raise Exception(f"invalid device selection: {args.device}")

    logging.info("The selected scene is %s", args.benchmark)
    benchmark = BENCHMARK_CONFIG[args.benchmark]
    download_scene(benchmark)
    executable_path, version = find_blender()

    logging.info("Starting benchmark!")
    start_time = time.time()
    score = run_blender_render(
        executable_path, LOG_DIRECTORY, args.device.upper(), benchmark
    )
    end_time = time.time()
    logging.info(
        f"Finished rendering {args.benchmark} in %d seconds", (end_time - start_time)
    )

    if score is None:
        raise Exception("no duration was found in the log to use as the score")

    report = {
        "test": "Blender Render",
        "test_parameter": args.benchmark,
        "score": score,
        "unit": "seconds",
        "version": version,
        "device": args.device,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging(LOG_DIRECTORY)
        main()
    except Exception as ex:
        logging.error("something went wrong running the benchmark!")
        logging.exception(ex)
        sys.exit(1)
