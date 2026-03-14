"""MSI Kombustor test script"""
from subprocess import Popen
import sys
from pathlib import Path
from msi_kombustor_utils import (
    parse_args,
    parse_resolution,
    parse_score,
    create_arg_string
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import (
    setup_logging,
    write_report_json,
    format_resolution)

INSTALL_DIR = r"C:\Program Files\Geeks3D\MSI Kombustor 4 x64"
EXECUTABLE = "MSI-Kombustor-x64.exe"

def main():
    """main"""
    args = parse_args()

    SCRIPT_DIRECTORY = Path(__file__).resolve().parent
    LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
    setup_logging(LOG_DIRECTORY)


    cmd = Path(INSTALL_DIR) / EXECUTABLE

    h, w = parse_resolution(args.resolution)
    argstr = create_arg_string(w, h, args.test, args.benchmark)

    with Popen([cmd, argstr]) as process:
        process.wait()

    log_path = Path(INSTALL_DIR) / "_kombustor_log.txt"
    score = parse_score(str(log_path))

    report = {
        "resolution": format_resolution(w, h),
        "test": args.test,
        "score": score
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    main()
