"""Tests for Steam helpers."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness_utils import steam


APP_ID = 1091500


def write_manifest(path: Path, installdir: str = "Cyberpunk 2077", buildid: str = "12345"):
    path.write_text(
        f'''"AppState"
{{
    "appid" "{APP_ID}"
    "installdir" "{installdir}"
    "buildid" "{buildid}"
}}
''',
        encoding="utf-8",
    )


class SteamHelperTests(unittest.TestCase):
    def test_linux_steam_root_discovery_uses_controlled_env_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            steam_root = Path(tmp) / "steam-root"
            (steam_root / "steamapps").mkdir(parents=True)

            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch.dict(os.environ, {"STEAM_DIR": str(steam_root)}):
                    paths = steam.get_steam_library_paths()

            self.assertEqual(paths, [steam_root])

    def test_manifest_install_location_and_build_id_parse_from_linux_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Steam"
            steamapps = root / "steamapps"
            common = steamapps / "common" / "Cyberpunk 2077"
            common.mkdir(parents=True)
            manifest = steamapps / f"appmanifest_{APP_ID}.acf"
            write_manifest(manifest, buildid="98765")

            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch.dict(os.environ, {"STEAM_DIR": str(root)}):
                    self.assertEqual(steam.get_app_manifest_path(APP_ID), manifest)
                    self.assertEqual(Path(steam.get_app_install_location(APP_ID)), common)
                    self.assertEqual(steam.get_build_id(APP_ID), "98765")

    def test_proton_prefix_uses_manifest_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Steam"
            steamapps = root / "steamapps"
            steamapps.mkdir(parents=True)
            manifest = steamapps / f"appmanifest_{APP_ID}.acf"
            write_manifest(manifest)

            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch.dict(os.environ, {"STEAM_DIR": str(root)}):
                    self.assertEqual(
                        steam.get_proton_prefix(APP_ID),
                        steamapps / "compatdata" / str(APP_ID) / "pfx",
                    )


if __name__ == "__main__":
    unittest.main()
