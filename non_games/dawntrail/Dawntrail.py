import logging
import sys
import time
import os
import shutil
import re
import zipfile
import pygetwindow as gw
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.paths import network_drive_path
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.input import user
from harness_utils.ocr_service import find_word
from harness_utils.report import seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "ffxiv-dawntrail-bench.exe"
DX_PROCESS_NAME = "ffxiv_dx11.exe"
ROOT_DIR = "C:/"


def delete_all_txt():
    directory = Path("C:/ffxiv-dawntrail-bench_v11/ffxiv-dawntrail-bench_v11/")
    for file in directory.glob("*.txt"):
        file.unlink(missing_ok=True)
    print("All .txt files deleted.")

def copy_from_network_drive() -> Path:
    """Copies ZIP from network drive and extracts it."""
    src_path = (
        network_drive_path()
        / "03_ProcessingFiles"
        / "ffxiv-dawntrail-bench_v11.zip"
    )
    zip_path = Path("C:/ffxiv-dawntrail-bench_v11.zip")
    extract_to = Path("C:/ffxiv-dawntrail-bench_v11")
    logging.info("Copying benchmark zip: %s -> %s", src_path, zip_path)
    # Copy the zip file
    shutil.copyfile(src_path, zip_path)
    # Extract it
    logging.info("Extracting to: %s", extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_to)
    logging.info("Extraction complete!")
    if zip_path.is_file():
        zip_path.unlink()# Deletes the file
        print(f"Deleted zip file: {zip_path.name}")
    else:
        print("Zip file not found")
    return extract_to

def get_results_txt():
    directory = Path("C:/ffxiv-dawntrail-bench_v11/ffxiv-dawntrail-bench_v11/")
    latest_txt = max(directory.glob("*.txt"),
    key=lambda f: f.stat().st_mtime,
    default=None)
    if not latest_txt:
        logging.info("No .txt result file found")
        return None
    return Path(directory) / latest_txt

def read_output_stats(path):
    if not FileExistsError(path):
        logging.info("File not found from path")
        sys.exit(1)
    latest_txt = path
    print(f"Reading results from: {latest_txt.name}")

    text = latest_txt.read_text(encoding="utf-8", errors="ignore")

    # Extract the values using regex
    score_match = re.search(r"Score:\s*(\d+)", text)
    resolution_match = re.search(r"Screen Size:\s*(\d+x\d+)", text)
    loading_match = re.search(r"Total Loading Time\s+(\d+\.?\d*)\s*sec", text)
    score = int(score_match.group(1)) if score_match else None
    resolution = resolution_match.group(1) if resolution_match else None
    total_loading_time = float(loading_match.group(1)) if loading_match else None
    return {
        "score": score,
        "resolution": resolution,
        "total_loading_time": total_loading_time,
        "file_path": str(latest_txt)
    }

def start_game():
    """Launch the benchmark executable."""
    logging.info("Starting Program...")

    # Minimize MarkBench window if present
    windows = gw.getWindowsWithTitle("Markbench")
    if windows:
        windows[0].minimize()

    os.startfile(r"C:\ffxiv-dawntrail-bench_v11\ffxiv-dawntrail-bench_v11\ffxiv-dawntrail-bench.exe")


def navigate_to_settings():
    """Navigate from main launcher menu to settings."""
    result = find_word("settings", timeout=10)
    user.click(int(result["x"]), int(result["y"]))


def navigate_settings() -> None:
    """Navigate through settings tabs."""
    navigate_to_settings()

    user.press("tab")
    time.sleep(0.5)

    am.take_screenshot("graphics.png", ArtifactType.CONFIG_IMAGE, "graphics settings menu")

    for _ in range(4):
        user.press("right")

    am.take_screenshot("display.png", ArtifactType.CONFIG_IMAGE, "display settings menu")

    for _ in range(3):
        user.press("right")

    for _ in range(9):
        user.press("tab")

    user.press("enter")


def run_benchmark():
    delete_all_txt()
    terminate_process(PROCESS_NAME)
    terminate_process(DX_PROCESS_NAME)
    #"""Run the full benchmark sequence."""
    setup_start_time = int(time.time())
    start_game()
    time.sleep(5)

    navigate_settings()

    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)

    # Start benchmark
    user.press("tab")
    user.press("down")
    user.press("down")

    result = find_word("start", timeout=10)
    start_pos = (result["x"], result["y"])

    user.press("up")
    user.press("up")
    user.click(start_pos[0], start_pos[1])

    test_start_time = int(time.time()) - 5
    logging.info("Benchmark started. Waiting for completion...")

    time.sleep(180)

    if not find_word("total", timeout=300, interval=0.5):
        logging.info("Did not see results screen. Marking as DNF.")
        sys.exit(1)

    time.sleep(5)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark")

    test_end_time = int(time.time()) - 2
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    time.sleep(3)
    result = find_word("save", timeout=30)
    user.click(result['x'], result['y'])
    logging.info("Saving results txt...")
    time.sleep(1)
    am.copy_file(get_results_txt(),ArtifactType.RESULTS_TEXT, "Results txt file" )
    return test_start_time, test_end_time


# ====================== Main Execution ======================
setup_logging(LOG_DIRECTORY)
am = ArtifactManager(LOG_DIRECTORY)

try:
    pathf = Path("C:/ffxiv-dawntrail-bench_v11")
    if pathf.exists():
        print("File already in C:/")
    else:
        print("No file found, copying from L:/ drive...")
        copy_from_network_drive()
    start_time, end_time = run_benchmark()
    logging.info(read_output_stats(get_results_txt()))
    resolutionf = read_output_stats(get_results_txt())['resolution']
    scoref = read_output_stats(get_results_txt())['score']
    load_time = read_output_stats(get_results_txt())['total_loading_time']

    report = {
        "score": str(load_time),
        "unit": "seconds",
        "fps_score": str(scoref),
        "resolution": str(resolutionf),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
    terminate_process(PROCESS_NAME)
    terminate_process(DX_PROCESS_NAME)
    terminate_process("Notepad.exe")

except Exception as e:
    logging.info("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    terminate_process(DX_PROCESS_NAME)
    sys.exit(1)
