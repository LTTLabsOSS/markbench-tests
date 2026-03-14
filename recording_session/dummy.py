"""Recording session test script"""
import logging
import os
from pathlib import Path
import socket
import sys
import time


PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import (
    setup_logging,
    write_report_json,
    seconds_to_milliseconds)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)

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
        
