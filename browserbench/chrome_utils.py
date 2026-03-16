"""Utilities for Google Chrome"""

import tempfile
import time
import json
import logging
import urllib.request
import subprocess
import winreg


def get_chrome_path_from_registry() -> str:
    """Finds the path to where Google Chrome is installed"""
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
    ]
    for key_path in reg_paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "")
                if value:
                    return value
        except FileNotFoundError:
            continue
    raise FileNotFoundError("Chrome executable not found in registry.")


def launch_chrome(chrome_path: str, url: str):
    """Launches Google Chrome in maximized window with minimal extras on a new profile"""
    profile_dir = tempfile.mkdtemp()
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [
            chrome_path,
            "--remote-debugging-port=9222",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-background-networking",
            f"--user-data-dir={profile_dir}",
            "--start-maximized",
            url,
        ]
    )
    return proc


def get_browser_websocket_url(target_url: str, retries=20) -> str:
    """Grabs the websocket url for the tab"""
    devtools_url = "http://localhost:9222/json"
    for _ in range(retries):
        try:
            with urllib.request.urlopen(devtools_url) as response:
                targets = json.load(response)

            for t in targets:
                if target_url in t.get("url", ""):
                    return t["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(1)
    raise RuntimeError("Failed to obtain DevTools websocket URL for tab")


def wait_for_ready(client, js_expr: str, retries=30, interval=1):
    """Ensures that the benchmark frontpage has finished loading before trying to start"""
    for _ in range(retries):
        res = client.call("Runtime.evaluate", {"expression": js_expr})
        val = res["result"]["result"].get("value")
        logging.debug("wait_for_ready check: %s -> %s", js_expr, val)
        if val:
            return
        time.sleep(interval)
    raise RuntimeError("Page did not reach ready state")


def get_browser_version(client):
    """Gets the Google Chrome version for traceability"""
    res = client.call("Browser.getVersion")
    return res["result"]["product"]


def run_js(client, expression: str):
    """Holdover run JavaScript function"""
    response = client.call(
        "Runtime.evaluate", {"expression": expression, "returnByValue": True}
    )

    if "result" in response and "result" in response["result"]:
        return response["result"]["result"].get("value")

    return None
