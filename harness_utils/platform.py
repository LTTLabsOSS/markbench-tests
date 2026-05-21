"""Platform detection helpers."""

import logging
import platform

logger = logging.getLogger(__name__)


def is_windows() -> bool:
    """Return True when running on Windows."""
    current_os = platform.system()
    result = current_os == "Windows"
    logger.debug("Checking Windows platform: os=%s result=%s", current_os, result)
    return result


def is_linux() -> bool:
    """Return True when running on Linux."""
    current_os = platform.system()
    result = current_os == "Linux"
    logger.debug("Checking Linux platform: os=%s result=%s", current_os, result)
    return result


def require_windows(feature: str) -> None:
    """Raise RuntimeError when a feature requires Windows but is not on Windows."""
    current_os = platform.system()
    logger.debug("Requiring Windows for feature=%s current_os=%s", feature, current_os)
    if current_os != "Windows":
        raise RuntimeError(f"{feature} requires Windows; current OS is {current_os}")


def require_linux(feature: str) -> None:
    """Raise RuntimeError when a feature requires Linux but is not on Linux."""
    current_os = platform.system()
    logger.debug("Requiring Linux for feature=%s current_os=%s", feature, current_os)
    if current_os != "Linux":
        raise RuntimeError(f"{feature} requires Linux; current OS is {current_os}")
