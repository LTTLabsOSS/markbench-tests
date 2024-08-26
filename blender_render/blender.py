"""Blender render test script"""
from blender_utils import find_blender, run_blender_render, download_scene
from argparse import ArgumentParser
import logging
import os.path
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from harness_utils.output import write_report_json, seconds_to_milliseconds


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIR, "run")
if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)
LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=LOGGING_FORMAT,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

VALID_DEVICES = ["CPU", "CUDA", "OPTIX", "HIP", "ONEAPI", "METAL"]
BENCHMARK_CONFIG = {
    "Barbershop": "barbershop_interior.blend",
    "Monster": "monster_under_the_bed_sss_demo_by_metin_seven.blend",
    "Junkshop": "Junkshop.blend",
    "BMW": "bmw27_cpu.blend",
    
}

parser = ArgumentParser()
parser.add_argument("-d", "--device", dest="device",
                    help="device", metavar="device", required=True)
parser.add_argument(
        "--benchmark", dest="benchmark", help="Benchmark test type", metavar="benchmark", required=True)
    

args = parser.parse_args()

if args.device not in VALID_DEVICES:
    logging.error("Invalid device selection!")
    sys.exit(1)

executable_path, version = find_blender()
benchmark = args.benchmark
logging.info(f"The selected scene is {benchmark}")
download_scene(benchmark)

try:
    logging.info('Starting benchmark!')
    start_time = time.time()
    benchmark= BENCHMARK_CONFIG[args.benchmark]
    score = run_blender_render(
        executable_path, LOG_DIRECTORY, args.device.upper(), benchmark)
    end_time = time.time()
    logging.info(f'Finished rendering {args.benchmark} in %d seconds', (end_time - start_time))

    if score is None:
        logging.error("No duration was found in the log to use as the score")
        sys.exit(1)

    report = {
        "test": f"Blender {args.benchmark} Render {args.device.upper()}",
        "score": score,
        "unit": "seconds",
        "version": version,
        "device": args.device,
        "benchmark": args.benchmark,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
