"""Asset path resolution helpers."""

import logging
import os
from pathlib import Path

from harness_utils.platform import is_windows

logger = logging.getLogger(__name__)


def resolve_asset(
    local_path: Path,
    env_var: str | None = None,
    fallback_network_path: Path | None = None,
) -> Path:
    """Resolve an asset from local, configured, or Windows network locations."""
    logger.info(
        "Resolving asset local_path=%s env_var=%s fallback_network_path=%s",
        local_path,
        env_var,
        fallback_network_path,
    )
    checked_paths: list[Path] = [local_path]

    logger.debug("Checking local asset path=%s", local_path)
    if local_path.exists():
        logger.info("Resolved asset from local path=%s", local_path)
        return local_path

    if env_var is not None:
        env_value = os.getenv(env_var)
        logger.debug("Checking asset environment variable env_var=%s value=%s", env_var, env_value)
        if env_value:
            env_path = Path(env_value).expanduser() / local_path.name
            checked_paths.append(env_path)
            logger.debug("Checking env asset path=%s", env_path)
            if env_path.exists():
                logger.info("Resolved asset from env path=%s", env_path)
                return env_path

    if fallback_network_path is not None and is_windows():
        checked_paths.append(fallback_network_path)
        logger.debug("Checking Windows network asset path=%s", fallback_network_path)
        if fallback_network_path.exists():
            logger.info("Resolved asset from Windows network path=%s", fallback_network_path)
            return fallback_network_path

    checked = ", ".join(str(path) for path in checked_paths)
    logger.warning("Asset not found; checked: %s", checked)
    raise FileNotFoundError(f"Asset not found; checked: {checked}")
