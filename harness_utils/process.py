"""Functions related to managing processes"""

import ctypes
import logging
import subprocess
import time

import psutil

from harness_utils.platform import is_windows

logger = logging.getLogger(__name__)


def terminate_process(process_name: str) -> None:
    """Finds a given process name and terminates it"""
    if not process_name:
        logger.debug("No process name provided")
        return

    logger.debug("Terminating process: %s", process_name)
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        if is_windows():
            command = process.info.get("name") or ""
        else:
            command = " ".join(process.info.get("cmdline") or [])

        if process_name.lower() in command.lower():
            logger.debug(
                "Terminating process pid=%s name=%s command=%s",
                process.info.get("pid"),
                process.info.get("name"),
                command,
            )
            try:
                process.terminate()
            except psutil.Error as err:
                logger.warning("Failed to terminate process: %s", err)

    logger.debug("Process termination complete")

def is_process_running(process_name):
    for process in psutil.process_iter(["pid", "name"]):
        process_name_current = process.info.get("name") or ""
        if process_name_current.lower() == process_name.lower():
            return process
    return None

def get_hwnds_for_pid(pid):
    hwnds = []

    def callback(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            current_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(current_pid)
            )

            if current_pid.value == pid:
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    # Get the window title for debugging
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value

                    hwnds.append((hwnd, title))
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), 0)

    return hwnds


def force_foreground(hwnd):
    """Bypass Windows foreground lock by simulating an ALT key press, then restore and foreground."""
    # 1. Restore the window in case it is minimized
    ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)

    # 2. Simulate ALT key down to bypass foreground lock
    ctypes.windll.user32.keybd_event(VK_MENU, 0, 0, 0)

    # 3. Set the foreground window
    result = ctypes.windll.user32.SetForegroundWindow(hwnd)

    # 4. Simulate ALT key up
    ctypes.windll.user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

    return bool(result)


def bring_process_front(process_name):
    target_process = is_process_running(process_name)

    if not target_process:
        return False

    # Get a list of tuples containing (hwnd, title)
    hwnds_with_titles = get_hwnds_for_pid(target_process.pid)

    if not hwnds_with_titles:
        return False

    # Try to find the window that actually has the Counter-Strike 2 title to avoid invisible dummy windows
    # If we can't find an exact match, we'll fall back to the first visible one we found
    target_hwnd = hwnds_with_titles[0][0]
    for hwnd, title in hwnds_with_titles:
        logger.info(f"Debug: Found window with title: '{title}'")
        if "Counter-Strike" in title:
            target_hwnd = hwnd
            break

    return force_foreground(target_hwnd)
