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
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        process_name_current = process.info.get("name") or ""
        if process_name_current.lower() == process_name.lower():
            return process
    return None


# def bring_process_front(process_name):
#     """bring the process to foreground"""
#     target_process = is_process_running(process_name)
#     subprocess.run(
#         [
#             "powershell.exe",
#             "-NoProfile",
#             "-Command",
#             f"(New-Object -ComObject WScript.Shell).AppActivate({target_process.pid})",
#         ],
#         check=False,
#     )


def bring_process_front(process_name):
    """Find the process by name, map its PID to an HWND, and foreground it."""
    target_process = is_process_running(process_name)

    if not target_process:
        return False

    # Map the process PID to its window handles
    hwnds = get_hwnds_for_pid(target_process.pid)

    if not hwnds:
        return False

    # Bring the first valid window associated with the PID to the front
    main_hwnd = hwnds[0]
    return bool(ctypes.windll.user32.SetForegroundWindow(main_hwnd))


def get_hwnds_for_pid(pid):
    """Find all visible window handles (HWNDs) associated with a PID."""
    hwnds = []

    def callback(hwnd, _):
        # Only look at visible windows
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            current_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(current_pid)
            )

            if current_pid.value == pid:
                # Filter out background/invisible overlays by ensuring the window has a title length
                if ctypes.windll.user32.GetWindowTextLengthW(hwnd) > 0:
                    hwnds.append(hwnd)
        return True

    # Define and call the C callback
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), 0)

    return hwnds
