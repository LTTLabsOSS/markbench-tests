"""Cross-platform helpers for Steam game and Windows-style user paths."""

import os
from pathlib import Path

from harness_utils.platform import is_linux, is_windows
from harness_utils.steam import get_app_install_location, get_proton_prefix

WINDOWS_NETWORK_DRIVE_ROOT = Path(r"\\labs.lmg.gg\labs")
LINUX_NETWORK_DRIVE_ROOT = Path("/mnt/labs.lmg.gg/labs")
PROTON_USERNAME = "steamuser"


def _require_app_id(app_id: int | None) -> int:
    if app_id is None:
        raise RuntimeError("Linux Proton path lookup requires app_id")
    return app_id


def _require_env_path(env_var: str) -> Path:
    value = os.getenv(env_var)
    if not value:
        raise RuntimeError(f"Missing environment variable: {env_var}")
    return _require_existing_path(Path(value))


def _require_existing_path(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(f"Missing path: {path}")
    return path


def proton_c_drive(app_id: int) -> Path:
    """Returns the Proton C: drive path for a Steam app."""
    return _require_existing_path(get_proton_prefix(app_id) / "drive_c")


def _proton_user_dir(app_id: int) -> Path:
    """Returns the default Proton Windows user path for a Steam app."""
    return _require_existing_path(proton_c_drive(app_id) / "users" / PROTON_USERNAME)


def local_appdata(app_id: int | None = None) -> Path:
    """Returns the native or Proton Local AppData path."""
    if is_windows():
        return _require_env_path("LOCALAPPDATA")
    if is_linux():
        return _require_existing_path(
            _proton_user_dir(_require_app_id(app_id)) / "AppData" / "Local"
        )
    raise RuntimeError("Local AppData lookup is only supported on Windows and Linux")


def user_documents(app_id: int | None = None) -> Path:
    """Returns the native or Proton user Documents path."""
    if is_windows():
        return _require_existing_path(_require_env_path("USERPROFILE") / "Documents")
    if is_linux():
        return _require_existing_path(
            _proton_user_dir(_require_app_id(app_id)) / "Documents"
        )
    raise RuntimeError("Documents lookup is only supported on Windows and Linux")


def network_drive_path() -> Path:
    """Returns the platform-specific Labs network drive path."""
    if is_windows():
        return WINDOWS_NETWORK_DRIVE_ROOT
    if is_linux():
        return LINUX_NETWORK_DRIVE_ROOT
    raise RuntimeError("Network drive lookup is only supported on Windows and Linux")


def game_install_path(app_id: int) -> Path:
    """Returns a Steam game install path."""
    return _require_existing_path(Path(get_app_install_location(app_id)))
