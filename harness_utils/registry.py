"""Cross-platform Windows and Proton registry readers."""

import logging
import re
from dataclasses import dataclass
from importlib import import_module
from typing import Literal

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

_WINE_VALUE_PATTERN = re.compile(r'^"((?:\\.|[^"])*)"=(.*)$')


@dataclass(frozen=True)
class RegistryEntry:
    """A registry value and its Windows registry type."""

    value: str | int
    kind: Literal["string", "dword", "qword"]


def _windows_registry_entry(value, value_type, winreg) -> RegistryEntry | None:
    if value_type == winreg.REG_DWORD and isinstance(value, int):
        return RegistryEntry(value=value, kind="dword")
    if value_type == winreg.REG_QWORD and isinstance(value, int):
        return RegistryEntry(value=value, kind="qword")
    if value_type in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) and isinstance(value, str):
        return RegistryEntry(value=value, kind="string")
    return None


def _read_windows_registry_key(key_path: str) -> dict[str, RegistryEntry]:
    winreg = import_module("winreg")
    entries: dict[str, RegistryEntry] = {}

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as registry_key:
            index = 0
            while True:
                try:
                    value_name, value, value_type = winreg.EnumValue(
                        registry_key, index
                    )
                except OSError:
                    break

                entry = _windows_registry_entry(value, value_type, winreg)
                if entry is not None:
                    entries[value_name] = entry
                index += 1
    except OSError as error:
        logger.error("Error reading registry key %s: %s", key_path, error)
        return {}

    return entries


def _unescape_wine_string(value: str) -> str:
    result: list[str] = []
    index = 0

    while index < len(value):
        character = value[index]
        if character == "\\" and index + 1 < len(value):
            next_character = value[index + 1]
            if next_character in ('"', "\\"):
                result.append(next_character)
                index += 2
                continue
        result.append(character)
        index += 1

    return "".join(result)


def _parse_wine_registry_entry(raw_value: str) -> RegistryEntry | None:
    value = raw_value.strip()
    folded_value = value.casefold()

    if folded_value.startswith("dword:"):
        try:
            return RegistryEntry(value=int(value.split(":", 1)[1], 16), kind="dword")
        except ValueError:
            return None

    if folded_value.startswith("hex(b):"):
        try:
            byte_values = bytes(
                int(part.strip(), 16)
                for part in value.split(":", 1)[1].split(",")
                if part.strip()
            )
        except ValueError:
            return None
        if len(byte_values) != 8:
            return None
        return RegistryEntry(
            value=int.from_bytes(byte_values, byteorder="little"), kind="qword"
        )

    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return RegistryEntry(value=_unescape_wine_string(value[1:-1]), kind="string")

    return None


def _read_proton_registry_key(registry_path, key_path: str) -> dict[str, RegistryEntry]:
    escaped_key_path = key_path.replace("\\", "\\\\").casefold()
    entries: dict[str, RegistryEntry] = {}
    in_requested_section = False
    found_requested_section = False

    try:
        with registry_path.open(encoding="utf-8") as registry_file:
            for raw_line in registry_file:
                line = raw_line.strip()
                if line.startswith("["):
                    closing_bracket = line.find("]")
                    if closing_bracket == -1:
                        in_requested_section = False
                        continue

                    section_name = line[1:closing_bracket].casefold()
                    in_requested_section = section_name == escaped_key_path
                    if in_requested_section:
                        found_requested_section = True
                    elif found_requested_section:
                        break
                    continue

                if not in_requested_section:
                    continue

                match = _WINE_VALUE_PATTERN.match(line)
                if match is None:
                    continue

                value_name = _unescape_wine_string(match.group(1))
                entry = _parse_wine_registry_entry(match.group(2))
                if entry is not None:
                    entries[value_name] = entry
    except OSError as error:
        logger.error("Error reading Proton registry key %s: %s", key_path, error)
        return {}

    if not found_requested_section:
        logger.error("Registry key not found: %s", key_path)
        return {}

    return entries


def read_registry_key(
    key_path: str, *, steam_app_id: int | None = None
) -> dict[str, RegistryEntry]:
    """Read all supported values from an HKCU key on Windows or Proton."""
    if is_windows():
        return _read_windows_registry_key(key_path)

    if is_linux():
        if steam_app_id is None:
            raise ValueError("steam_app_id is required to read a Proton registry key")
        from harness_utils.steam import get_proton_prefix

        registry_path = get_proton_prefix(steam_app_id) / "user.reg"
        return _read_proton_registry_key(registry_path, key_path)

    raise RuntimeError("Registry access is only supported on Windows and Linux")


def read_registry_value(
    key_path: str,
    value_name: str,
    *,
    steam_app_id: int | None = None,
) -> str | int | None:
    """Read one supported value from an HKCU key on Windows or Proton."""
    entries = read_registry_key(key_path, steam_app_id=steam_app_id)
    folded_value_name = value_name.casefold()

    for entry_name, entry in entries.items():
        if entry_name.casefold() == folded_value_name:
            return entry.value

    logger.error("Registry value not found: %s\\%s", key_path, value_name)
    return None
