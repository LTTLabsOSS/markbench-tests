"""Cross-platform helpers for Steam game and Windows-style user paths."""

import os
from pathlib import Path

from harness_utils.platform import is_linux, is_windows
from harness_utils.steam import get_app_install_location, get_proton_prefix

WINDOWS_NETWORK_DRIVE_ROOT = Path(r"\\labs.lmg.gg\labs")
LINUX_NETWORK_DRIVE_ROOT = Path("/mnt/labs.lmg.gg/labs")
PROTON_USERNAME = "steamuser"


def _proton_user_dir(app_id: int | None) -> Path:
    """Return the Proton Windows user directory for a Steam app."""
    if app_id is None:
        raise RuntimeError("Linux Proton path lookup requires app_id")

    path = get_proton_prefix(app_id) / "drive_c" / "users" / PROTON_USERNAME
    if not path.exists():
        raise RuntimeError(f"Missing path: {path}")
    return path


def local_appdata(app_id: int | None = None) -> Path:
    """Return the native or Proton Local AppData path."""
    if is_windows():
        path = os.getenv("LOCALAPPDATA")
        if not path:
            raise RuntimeError("Missing environment variable: LOCALAPPDATA")
        return Path(path)
    if is_linux():
        return _proton_user_dir(app_id) / "AppData" / "Local"
    raise RuntimeError("Local AppData lookup is only supported on Windows and Linux")


def user_documents(app_id: int | None = None) -> Path:
    """Return the native or Proton user Documents path."""
    if is_windows():
        path = os.getenv("USERPROFILE")
        if not path:
            raise RuntimeError("Missing environment variable: USERPROFILE")
        return Path(path) / "Documents"
    if is_linux():
        return _proton_user_dir(app_id) / "Documents"
    raise RuntimeError("Documents lookup is only supported on Windows and Linux")


def user_saved_games(app_id: int | None = None) -> Path:
    """Return the native or Proton user Saved Games path."""
    if is_windows():
        path = os.getenv("USERPROFILE")
        if not path:
            raise RuntimeError("Missing environment variable: USERPROFILE")
        return Path(path) / "Saved Games"
    if is_linux():
        return _proton_user_dir(app_id) / "Saved Games"
    raise RuntimeError("Saved Games lookup is only supported on Windows and Linux")


def network_drive_path() -> Path:
    """Return the platform-specific Labs network drive path."""
    if is_windows():
        return WINDOWS_NETWORK_DRIVE_ROOT
    if is_linux():
        return LINUX_NETWORK_DRIVE_ROOT
    raise RuntimeError("Network drive lookup is only supported on Windows and Linux")


def game_install_path(app_id: int) -> Path:
    """Return a Steam game install path."""
    path = Path(get_app_install_location(app_id))
    if not path.exists():
        raise RuntimeError(f"Missing path: {path}")
    return path
