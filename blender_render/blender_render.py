"""Blender render test script"""

import logging
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from blender_render_utils import (
    BENCHMARK_CONFIG,
    download_scene,
    find_blender,
    run_blender_render,
)

sys.path.insert(1, str(Path(sys.path[0]).parent.parent))
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    write_report_json,
)

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")


def setup_logging():
    """default logging config"""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=f"{LOG_DIR}/harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


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
    score = run_blender_render(executable_path, LOG_DIR, args.device.upper(), benchmark)
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

    write_report_json(str(LOG_DIR), "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("something went wrong running the benchmark!")
        logging.exception(ex)
        sys.exit(1)
