import logging
import re
import sys
import time
import os
import subprocess
import shutil
from pathlib import Path

import win32com.client
from argparse import ArgumentParser

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.paths import network_drive_path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
ntwrk_src_path = network_drive_path() / "03_ProcessingFiles" / "SSD Video" / "drivevideo.mp4"
dest_path = r"C:\test_video"

def _parse_csv_line(line):
    fields = []
    field = []
    in_quotes = False
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    field.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                field.append(ch)
        else:
            if ch == '"':
                in_quotes = True
            elif ch == ',':
                fields.append(''.join(field))
                field = []
            else:
                field.append(ch)
        i += 1
    fields.append(''.join(field))
    return fields
 
 
def _to_float(val):
    if val is None:
        return None
    val = val.strip()
    if val == "":
        return None
    try:
        return float(val)
    except ValueError:
        return None
 
 
def _col_values(data_rows, idx):
    return [row[idx] if idx < len(row) else "" for row in data_rows]
 
 
def _last_nonempty(data_rows, idx):
    last_val = None
    for row in data_rows:
        v = row[idx] if idx < len(row) else ""
        if v is not None and v.strip() != "":
            last_val = v
    return last_val.strip() if last_val else None
 
 
def _extract_letter(descriptor):
    # Matches the trailing "[C:]" / "[D:]" style drive-letter tag
    m = re.search(r"\[([A-Za-z]):\]", descriptor or "")
    return f"{m.group(1).upper()}:" if m else None
 
 
def _normalize_letter(letter):
    if letter is None:
        return None
    letter = letter.strip().upper()
    if not letter.endswith(":"):
        letter += ":"
    return letter
 
 
def _build_drives(raw_header, data_rows, read_col_name, write_col_name):
    """Match Read/Write Rate columns that share the same footer descriptor
    (the actual drive identity string) into one entry per drive."""
    read_indices = [i for i, h in enumerate(raw_header) if h == read_col_name]
    write_indices = [i for i, h in enumerate(raw_header) if h == write_col_name]
 
    drives_by_descriptor = {}
    for idx in read_indices:
        desc = _last_nonempty(data_rows, idx)
        if desc is not None:
            drives_by_descriptor.setdefault(desc, {})["read_idx"] = idx
    for idx in write_indices:
        desc = _last_nonempty(data_rows, idx)
        if desc is not None:
            drives_by_descriptor.setdefault(desc, {})["write_idx"] = idx
 
    drives = [
        {
            "name": desc,
            "letter": _extract_letter(desc),
            "read_idx": idxs.get("read_idx"),
            "write_idx": idxs.get("write_idx"),
        }
        for desc, idxs in drives_by_descriptor.items()
    ]
    drives.sort(key=lambda d: (d["read_idx"] if d["read_idx"] is not None else 1 << 30))
    return drives
 
 
def _collect_rates(data_rows, drives, target_omit):
    read_vals = []
    write_vals = []
    for d in drives:
        if target_omit is not None and d["letter"] == target_omit:
            continue  # omit this drive's data, but it stays in `drives`
        if d["read_idx"] is not None:
            read_vals.extend(
                v for v in (_to_float(x) for x in _col_values(data_rows, d["read_idx"])) if v is not None
            )
        if d["write_idx"] is not None:
            write_vals.extend(
                v for v in (_to_float(x) for x in _col_values(data_rows, d["write_idx"])) if v is not None
            )
    return read_vals, write_vals
 
 
def analyze_drive_rates(csv_path: str, sourceletter: str = None):
    """
    Reads an HWiNFO-style CSV log (no external libraries). Detects all drives
    present via duplicate 'Read Rate [MB/s]' / 'Write Rate [MB/s]' column
    pairs (one pair per monitored drive), identifies each drive's letter
    from its footer descriptor (e.g. '...[C:]'), and computes avg_read /
    avg_write using only the drive(s) that do NOT match `sourceletter`.
 
    `sourceletter` behaves as the drive to OMIT from the averages
    (e.g. "D:" or "D"). Its name is still reported in `drives`.
    If `sourceletter` is None, all detected drives are included.
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        raw_lines = [line.rstrip('\n').rstrip('\r') for line in f]
 
    lines = [ln for ln in raw_lines if ln != ""]
    if not lines:
        return {"avg_read": None, "avg_write": None, "drives": []}
 
    rows = [_parse_csv_line(ln) for ln in lines]
    raw_header = [h.strip() for h in rows[0]]
    data_rows = rows[1:]
 
    drives = _build_drives(raw_header, data_rows, "Read Rate [MB/s]", "Write Rate [MB/s]")
 
    target_omit = _normalize_letter(sourceletter)
    read_vals, write_vals = _collect_rates(data_rows, drives, target_omit)
 
    avg_read = sum(read_vals) / len(read_vals) if read_vals else None
    avg_write = sum(write_vals) / len(write_vals) if write_vals else None
 
    return {
        "avg_read": avg_read,
        "avg_write": avg_write,
        "drives": [{"name": d["name"], "letter": d["letter"]} for d in drives],
    }

def copy_from_network_drive(path):
    if not Path(path).is_file():
        """Copies video file from network drive to the source drive."""
        logging.info("File not found on source drive. Attempting file copy")
        shutil.copyfile(ntwrk_src_path, path)
        if path.is_file():
            logging.info("File successfully copied to source drive")
            return path
        else:
            logging.info("Some issue prevented network transfer...")
            return
    else:
        logging.info("File already exists on source drive, skipping copy.")
        return path

def get_args_drive():
    """Gets script arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--driveletter",
        dest="driveletter",
        help="Source drive letter"
    )
    logging.info(vars(parser.parse_args())['driveletter'])
    return vars(parser.parse_args())['driveletter']

def run_benchmark(filepath):
    """Copies file from specified drive and extracts it."""
    if Path(dest_path).is_dir():
        logging.info(f"Destination dir found, continuing: {Path(dest_path).name}")
    else:
        logging.info("Destination dir not found... Creating...")
        os.makedirs(dest_path, exist_ok=True)
    logging.info("Starting HWiNFO...")
    process = subprocess.Popen(
    [
        r"C:\Markbench\hwinfo_cli\hwinfo_cli.exe",
        "--out", r"C:\Markbench\harnesses\filetransfer\run\drives.csv",
        "--poll-ms", "200",
        "--all-sensors"
    ],
    stdin=subprocess.PIPE,  # Crucial for sending commands
    text=True,              # Sends input as strings instead of raw bytes
    bufsize=1               # Line-buffered for immediate transmission
    )

    logging.info("Copying benchmark file: %s -> %s", filepath, dest_path)
    test_start_time = int(time.time())
    # Copy the file
    # Launch the native Windows Explorer copy operation
    logging.info("Copying...")
    shell = win32com.client.Dispatch("Shell.Application")
    shell.NameSpace(dest_path).CopyHere(filepath)
    process.stdin.write("stop\n")  # \n simulates hitting the Enter key
    process.stdin.flush()          # Forces the string out of Python's buffer
    file_path = str(dest_path) + r"\drivevideo.mp4"
    # Deletes the file after the test
    test_end_time = int(time.time())
    if Path(file_path).is_file():
        Path(file_path).unlink()
        logging.info(f"Deleted file: {Path(dest_path).name}")
    else:
        logging.info("File not found... Some error during file transfer.")
    return test_start_time, test_end_time

#MAIN

setup_logging(LOG_DIRECTORY)
am = ArtifactManager(LOG_DIRECTORY)

src_path = str(get_args_drive()) + r"\drivevideo.mp4"
start_time, end_time = run_benchmark(copy_from_network_drive(src_path))
avg_read = analyze_drive_rates(r"C:\Markbench\harnesses\filetransfer\run\drives.csv", get_args_drive())['avg_read']
avg_write = analyze_drive_rates(r"C:\Markbench\harnesses\filetransfer\run\drives.csv", get_args_drive())['avg_write']
write_drive_name = analyze_drive_rates(r"C:\Markbench\harnesses\filetransfer\run\drives.csv", get_args_drive())['drives'][0]['name']
read_drive_name = analyze_drive_rates(r"C:\Markbench\harnesses\filetransfer\run\drives.csv", get_args_drive())['drives'][1]['name']
report = {
        "score": avg_write,
        "unit": "MB/s",
        "read_score": avg_read,
        "unit": "MB/s",
        "target_drive": write_drive_name,
        "source_drive": read_drive_name,
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
}


am.create_manifest()
write_report_json(LOG_DIRECTORY, "report.json", report)
