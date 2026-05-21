"""Asset path resolution helpers."""

import os
from pathlib import Path

from harness_utils.platform import is_windows


def resolve_asset(
    local_path: Path,
    env_var: str | None = None,
    fallback_network_path: Path | None = None,
) -> Path:
    """Resolve an asset from local, configured, or Windows network locations."""
    checked_paths: list[Path] = [local_path]

    if local_path.exists():
        return local_path

    if env_var is not None:
        env_value = os.getenv(env_var)
        if env_value:
            env_path = Path(env_value).expanduser() / local_path.name
            checked_paths.append(env_path)
            if env_path.exists():
                return env_path

    if fallback_network_path is not None and is_windows():
        checked_paths.append(fallback_network_path)
        if fallback_network_path.exists():
            return fallback_network_path

    checked = ", ".join(str(path) for path in checked_paths)
    raise FileNotFoundError(f"Asset not found; checked: {checked}")
