"""Cross-platform helpers for Windows game paths and Proton prefixes."""

import logging
import os
from pathlib import Path

from harness_utils.platform import is_linux, is_windows
from harness_utils.steam import get_app_install_location, get_proton_prefix

logger = logging.getLogger(__name__)


def _require_app_id(app_id: int | None, feature: str) -> int:
    logger.debug("Checking app_id for feature=%s app_id=%s", feature, app_id)
    if app_id is None:
        raise RuntimeError(f"{feature} requires app_id on Linux")
    return app_id


def _require_env_path(env_var: str) -> Path:
    logger.info("Resolving Windows environment path env_var=%s", env_var)
    value = os.getenv(env_var)
    if not value:
        raise RuntimeError(f"Missing environment variable: {env_var}")
    return _require_existing_path(Path(value))


def _require_existing_path(path: Path) -> Path:
    logger.debug("Checking path exists: %s", path)
    if not path.exists():
        raise RuntimeError(f"Missing path: {path}")
    return path


def _windows_userprofile_path(folder_name: str) -> Path:
    logger.info("Resolving Windows user profile path folder=%s", folder_name)
    userprofile = _require_env_path("USERPROFILE")
    return _require_existing_path(userprofile / folder_name)


def _proton_user_dir(app_id: int) -> Path:
    logger.info("Resolving Proton user directory app_id=%s", app_id)
    prefix = _require_existing_path(get_proton_prefix(app_id))
    users_dir = _require_existing_path(prefix / "drive_c" / "users")
    steamuser = users_dir / "steamuser"
    logger.debug("Checking Proton steamuser path: %s", steamuser)
    if steamuser.exists():
        logger.info("Using Proton steamuser directory: %s", steamuser)
        return steamuser

    candidates = sorted(
        (
            path
            for path in users_dir.iterdir()
            if path.is_dir() and path.name.lower() != "public"
        ),
        key=lambda path: path.name.lower(),
    )
    if candidates:
        logger.info("Using first Proton user directory: %s", candidates[0])
        return candidates[0]

    raise RuntimeError(f"Missing Proton user directory under: {users_dir}")


def _proton_user_path(app_id: int | None, *parts: str) -> Path:
    logger.info("Resolving Proton Windows path app_id=%s parts=%s", app_id, parts)
    linux_app_id = _require_app_id(app_id, "Proton Windows path lookup")
    return _require_existing_path(_proton_user_dir(linux_app_id).joinpath(*parts))


def windows_local_appdata(app_id: int | None = None) -> Path:
    """Returns the native or Proton Windows Local AppData path."""
    logger.info("Resolving Windows Local AppData app_id=%s", app_id)
    if is_windows():
        return _require_env_path("LOCALAPPDATA")
    if is_linux():
        return _proton_user_path(app_id, "AppData", "Local")
    raise RuntimeError("Windows Local AppData lookup is only supported on Windows and Linux")


def windows_roaming_appdata(app_id: int | None = None) -> Path:
    """Returns the native or Proton Windows Roaming AppData path."""
    logger.info("Resolving Windows Roaming AppData app_id=%s", app_id)
    if is_windows():
        return _require_env_path("APPDATA")
    if is_linux():
        return _proton_user_path(app_id, "AppData", "Roaming")
    raise RuntimeError("Windows Roaming AppData lookup is only supported on Windows and Linux")


def windows_documents(app_id: int | None = None) -> Path:
    """Returns the native or Proton Windows Documents path."""
    logger.info("Resolving Windows Documents app_id=%s", app_id)
    if is_windows():
        return _windows_userprofile_path("Documents")
    if is_linux():
        return _proton_user_path(app_id, "Documents")
    raise RuntimeError("Windows Documents lookup is only supported on Windows and Linux")


def windows_saved_games(app_id: int | None = None) -> Path:
    """Returns the native or Proton Windows Saved Games path."""
    logger.info("Resolving Windows Saved Games app_id=%s", app_id)
    if is_windows():
        return _windows_userprofile_path("Saved Games")
    if is_linux():
        return _proton_user_path(app_id, "Saved Games")
    raise RuntimeError("Windows Saved Games lookup is only supported on Windows and Linux")


def game_install_path(app_id: int) -> Path:
    """Returns a Steam game install path."""
    logger.info("Resolving game install path app_id=%s", app_id)
    path = _require_existing_path(Path(get_app_install_location(app_id)))
    logger.info("Resolved game install path app_id=%s path=%s", app_id, path)
    return path
