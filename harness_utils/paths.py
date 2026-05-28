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
    logger.info("Resolving Proton user path app_id=%s parts=%s", app_id, parts)
    linux_app_id = _require_app_id(app_id, "Proton path lookup")
    return _require_existing_path(_proton_user_dir(linux_app_id).joinpath(*parts))


def local_appdata(
    app_id: int | None = None,
    *parts: str,
    must_exist: bool = False,
) -> Path:
    """Returns the native or Proton Local AppData path."""
    logger.info(
        "Resolving Local AppData app_id=%s parts=%s must_exist=%s",
        app_id,
        parts,
        must_exist,
    )
    if is_windows():
        path = _require_env_path("LOCALAPPDATA").joinpath(*parts)
        if must_exist:
            path = _require_existing_path(path)
        logger.info("Resolved path=%s", path)
        return path
    if is_linux():
        path = _proton_user_path(app_id, "AppData", "Local").joinpath(*parts)
        if must_exist:
            path = _require_existing_path(path)
        logger.info("Resolved path=%s", path)
        return path
    raise RuntimeError("Local AppData lookup is only supported on Windows and Linux")


def game_install_path(
    app_id: int,
    *parts: str,
    must_exist: bool = False,
) -> Path:
    """Returns a Steam game install path."""
    logger.info(
        "Resolving game install path app_id=%s parts=%s must_exist=%s",
        app_id,
        parts,
        must_exist,
    )
    root = _require_existing_path(Path(get_app_install_location(app_id)))
    path = root.joinpath(*parts)
    if must_exist:
        path = _require_existing_path(path)
    logger.info("Resolved game install path app_id=%s path=%s", app_id, path)
    return path
