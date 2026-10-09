"""godot compile test script"""

import logging
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

from godot_compile_utils import (
    GODOT_VERSION,
    LLVM_MINGW_HOSTS,
    convert_duration_string_to_seconds,
    copy_godot_source_from_network_drive,
    create_conda_environment,
    get_compiler_version,
    install_llvm_mingw,
    install_miniconda,
    run_conda_command,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from godot_compile_utils import current_time_ms

from harness_utils.output_logging import setup_logging
from harness_utils.report import write_report_json

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"

parser = ArgumentParser()
parser.add_argument(
    "-a",
    "--architecture",
    dest="architecture",
    help="Architecture type",
    required=True,
    choices=LLVM_MINGW_HOSTS.keys(),
)
args = parser.parse_args()


def main():
    """test script entry point"""
    setup_logging(LOG_DIRECTORY)
    output = install_llvm_mingw(args.architecture)
    logger.info(output)

    compiler = get_compiler_version(args.architecture)
    logger.info("compiler: %s", compiler)

    output = install_miniconda()
    logger.info(output)

    output = copy_godot_source_from_network_drive()
    logger.info(output)

    output = create_conda_environment()
    logger.info(output)

    output = run_conda_command(["-m", "pip", "install", "scons"])
    logger.info(output)

    build_options = [
        "platform=windows",
        f"arch={args.architecture}",
        "use_mingw=yes",
        "use_llvm=yes",
        # the d3d12 driver needs an sdk downloaded at build time, so leave it out
        "d3d12=no",
        # no mingw_prefix: godot splits the tool path with shlex, which strips
        # windows backslashes, so the toolchain is found via PATH instead
        # (install_llvm_mingw puts its bin folder first)
    ]

    output = run_conda_command(["-m", "SCons", "--clean", "--no-cache"] + build_options)
    logger.info(output)

    start_time = current_time_ms()
    output = run_conda_command(["-m", "SCons", "--no-cache"] + build_options)
    logger.info(output)
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
        "version": GODOT_VERSION,
        "architecture": args.architecture,
        "compiler": compiler,
        "end_time": end_time,
        "score": score,
        "unit": "seconds",
        "test": f"Godot {GODOT_VERSION.removesuffix('-stable')} Compile",
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.error("error running benchmark")
        logger.exception("Unhandled exception")
        sys.exit(1)
