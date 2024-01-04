"""Recording session test script"""
import logging
import os
import socket
import sys
import time


sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import (
    write_report_json,
    setup_log_directory,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIR, "run")
setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

HOST = ''
PORT = 30000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_time = time.time()
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    logging.error("Bind failed %s", msg)
    sys.exit(1)

s.listen(1)
while True:
    time.sleep(0.1)
    conn, addr = s.accept()
    if conn:
        stop_time = time.time()
        report = {
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(stop_time)
        }

        write_report_json(LOG_DIRECTORY, "report.json", report)
        sys.exit(0)