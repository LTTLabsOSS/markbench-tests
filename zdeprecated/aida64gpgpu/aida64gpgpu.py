'''Aida64 GPGPU test script'''
import logging
import os
import subprocess
import sys

INSTALL_DIR = "C:\\Program Files\\Aida64Business\\aida64business675"
EXECUTABLE = "aida64.exe"

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)
LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=LOGGING_FORMAT,
                    datefmt='%m-%d %H:%M',
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

executable = os.path.join(INSTALL_DIR, EXECUTABLE)
report_dest = os.path.join(log_dir, "report.xml")
argstr = f"/GGBENCH {report_dest}"
result = subprocess.run([executable, "/GGBENCH", report_dest], check=False)

if result.returncode > 0:
    logging.error("Aida failed with exit code {result.returncode}")
    logging.warning(result.stdout)
    logging.warning(result.stderr)
    sys.exit(1)
