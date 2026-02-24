"""Multi-Benchmark Browser Harness"""
import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

from cdp_client import CDPClient
from chrome_utils import get_chrome_path_from_registry, launch_chrome, get_browser_websocket_url, wait_for_ready, get_browser_version, run_js

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    write_report_json,
    seconds_to_milliseconds
)

INTERNAL_TIMEOUT = 900  # 15 minutes
script_dir = Path(__file__).resolve().parent
log_dir = script_dir / "run"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "harness.log"
logging.basicConfig(
    filename=log_file,
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

BENCHMARKS = {
    "jetstream2": {
        "url": "https://browserbench.org/JetStream/",
        "wait_expr": "document.querySelector('#status a.button[href^=\"javascript:JetStream.start()\"]') != null",
        "start_expr": "JetStream.start(); true;",
        "score_expr": """
            (function() {
                const el = document.querySelector('#result-summary.done .score');
                return el ? parseFloat(el.innerText) : null;
            })();
        """,
        "version": "2.2"
    },
    "speedometer": {
        "url": "https://browserbench.org/Speedometer3.1/",
        "wait_expr": "document.querySelector('.start-tests-button') != null",
        "start_expr": "document.querySelector('.start-tests-button').click(); true;",
        "score_expr": """
            (function() {
                const el = document.querySelector('#result-number');
                return el ? parseFloat(el.innerText) : null;
            })();
        """,
        "version": "3.1"
    },
    "motionmark": {
        "url": "https://browserbench.org/MotionMark1.3.1/",
        "wait_expr": "document.querySelector('#start-button') != null",
        "start_expr": "document.querySelector('#start-button').click(); true;",
        "score_expr": """
            (function() {
                const el = document.querySelector('.score');
                if (!el) return null;
                const val = el.innerText.split('@')[0].trim();
                const num = parseFloat(val);
                return isNaN(num) ? null : num;
            })();
        """,
        "version": "1.3.1"
    },
    "kraken": {
        "landing_url": "https://mozilla.github.io/krakenbenchmark.mozilla.org/",
        "wait_expr_landing": "document.querySelector('a[href$=\"driver.html\"]') != null",
        "start_expr_landing": "document.querySelector('a[href$=\"driver.html\"]').click(); true;",
        "url": "https://mozilla.github.io/krakenbenchmark.mozilla.org/kraken-1.1/driver.html",
        "wait_expr": "!!document.querySelector('#run')",
        "start_expr": "document.querySelector('#run').click(); true;",
        "score_expr": """
            (function() {
                const pre = document.querySelector('#console');
                if (!pre) return null;
                const match = pre.innerText.match(/Total:\\s+([0-9.]+)ms/);
                return match ? parseFloat(match[1]) : null;
            })();
        """,
        "version": "1.1"
    },
    "webxprt": {
        "url": "https://www.principledtechnologies.com/benchmarkxprt/webxprt/2021/wx4_build_3_7_3/",
        "wait_expr": "!!document.querySelector('button.wx-start_btn[data-start-test]')",
        "start_expr": "document.querySelector('button.wx-start_btn[data-start-test]').click(); true;",
        "score_expr": """
            (function() {
                const el = document.querySelector('.wx-results-score-text');
                if (!el) return null;
                const val = el.innerText.trim();
                const num = parseFloat(val);
                return isNaN(num) ? null : num;
            })();
        """,
        "version": "3.7.3"
    }
}

def start_benchmark(client: CDPClient, start_expr: str):
    client.call("Runtime.evaluate", {"expression": start_expr})

def wait_for_score(client: CDPClient, score_expr: str) -> float:
    start_time = time.time()
    while time.time() - start_time < INTERNAL_TIMEOUT:
        res = client.call("Runtime.evaluate", {"expression": score_expr})
        val = res["result"]["result"].get("value")
        if val is not None:
            return float(val)
        time.sleep(3)
    raise TimeoutError("Benchmark did not finish in time")

def main():
    # Determine units based on benchmark
    
    parser = argparse.ArgumentParser(description="Browser benchmark harness")
    parser.add_argument("--benchmark", choices=BENCHMARKS.keys(), required=True,
                        help="Which benchmark to run")
    args = parser.parse_args()
    bench = BENCHMARKS[args.benchmark]

    try:
        logging.info("Detecting Chrome path...")
        chrome_path = get_chrome_path_from_registry()
        logging.info("Chrome path: %s", chrome_path)

        # Determine initial URL
        initial_url = bench.get("landing_url", bench["url"])
        logging.info("Launching isolated Chrome instance...")
        chrome_proc, profile_dir = launch_chrome(chrome_path, initial_url)

        # Connect CDP
        ws_url = get_browser_websocket_url(initial_url)
        client = CDPClient(ws_url)
        client.connect()

        if args.benchmark == "kraken":
            # Wait for landing page link
            wait_for_ready(client, bench["wait_expr_landing"])
            logging.info("Kraken landing page ready. Pausing 10s before clicking 'Begin'...")
            time.sleep(10)

            # Click Begin link
            START_TIME = time.time()
            start_benchmark(client, bench["start_expr_landing"])
            logging.info("Clicked 'Begin', driver page now loading...'")

            # Reconnect to driver tab
            ws_url = get_browser_websocket_url(bench["url"])
            client = CDPClient(ws_url)
            client.connect()

            # Wait for page to fully load (driver page DOM ready)
            wait_for_ready(client, "document.readyState === 'complete'")
            logging.info("Kraken driver page loaded and running benchmark.")
            
            unit = "ms"
        else:
            # Wait for benchmark start
            wait_for_ready(client, bench["wait_expr"])
            time.sleep(10)  # settle
            

            START_TIME = time.time()
            start_benchmark(client, bench["start_expr"])
            unit = "score"

        browser_version = get_browser_version(client)
        logging.info("Browser version: %s", browser_version)

        score = wait_for_score(client, bench["score_expr"])
        END_TIME = time.time()

        logging.info("%s score: %s", args.benchmark, score)

        # JSON reporting
        report = {
            "test": "Browser Benchmark",
            "benchmark": args.benchmark,
            "benchmark_version": bench.get("version", "unknown"),
            "score": score,
            "unit": unit,
            "browser_version": browser_version,
            "start_time": seconds_to_milliseconds(START_TIME),
            "end_time": seconds_to_milliseconds(END_TIME)
        }

        write_report_json(str(log_dir), "report.json", report)

        time.sleep(15)

        # Terminate Chrome
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            chrome_proc.kill()

    except Exception as e:
        logging.error("Error during benchmark!")
        logging.exception(e)
        if "chrome_proc" in locals():
            chrome_proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()