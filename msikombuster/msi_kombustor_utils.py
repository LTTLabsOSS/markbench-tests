"""Utility functions for MSI Kombustor test script"""
from argparse import ArgumentParser, Namespace
import re

# cSpell:disable
avail_tests = [
    "vkfurrytorus",
    "glfurrytorus",
    "vkfurrymsi",
    "glfurrymsi",
    "glfurmark1700mb",
    "glfurmark3200mb",
    "glfurmark5200mb",
    "glfurmark6500mb",
    "glmsi01burn",
    "glmsi01",
    "glmsi02cpumedium",
    "glmsi02cpumedium++",
    "glmsi02gpumedium",
    "glmsi02gpumedium++",
    "glmsi02cpuhard",
    "glmsi02gpuhard",
    "glphongdonut",
    "vkphongdonut",
    "glpbrdonut",
    "vktessyspherex32",
    "vktessyspherex16",
    "gltessyspherex32",
    "gltessyspherex16",
]
# cSpell:enable

def parse_args() -> Namespace:
    """Gets script arguments"""
    parser = ArgumentParser()
    parser.add_argument("-t", "--test", dest="test", choices=avail_tests,
                        help="kombustor test", metavar="test", required=True)
    parser.add_argument("-r", "--resolution", dest="resolution",
                        help="resolution", metavar="resolution", required=True)
    parser.add_argument("-b", "--benchmark", dest="benchmark",
                        help="benchmark mode", metavar="benchmark", required=False)
    return parser.parse_args()


def parse_resolution(arg: str) -> tuple[str, str]:
    """Gets individual height and width values from resolution string"""
    match = re.search(r"^\d+,\d+$", arg)
    if match is None:
        raise ValueError("Resolution value must be in format height,width")
    resolution = arg.split(",")
    height = resolution[0]
    width = resolution[1]

    return height, width


def parse_score(log_path: str):
    """Parses score value from log file"""
    pattern = re.compile(r"score => (\d+)")
    with open(log_path, encoding="utf-8") as log:
        lines = log.readlines()
        for line in reversed(lines):
            match = pattern.search(line)
            if match:
                return match.group(1)
    return "N/A"


def create_arg_string(width: str, height: str, test: str, benchmark: str) -> str:
    """Create string for Kombustor CLI arguments"""
    arg_string = f"-width={width} -height={height} -{test} -logfile_in_app_folder "
    if benchmark == "true":
        arg_string += "-benchmark"
    return arg_string
