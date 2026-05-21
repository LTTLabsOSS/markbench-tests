"""Tests for Windows and Proton path helpers."""

import tempfile
import unittest
import re
from pathlib import Path
from unittest.mock import patch

from harness_utils import paths


APP_ID = 1091500


def create_proton_user(prefix: Path, username: str) -> Path:
    user_dir = prefix / "drive_c" / "users" / username
    for child in [
        user_dir / "AppData" / "Local",
        user_dir / "AppData" / "Roaming",
        user_dir / "Documents",
        user_dir / "Saved Games",
    ]:
        child.mkdir(parents=True)
    return user_dir


class PathHelperTests(unittest.TestCase):
    def test_linux_requires_app_id_for_windows_paths(self):
        with patch("harness_utils.platform.platform.system", return_value="Linux"):
            with self.assertRaisesRegex(RuntimeError, "requires app_id"):
                paths.windows_local_appdata()

    def test_proton_user_dir_prefers_steamuser(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp) / "pfx"
            (prefix / "drive_c" / "users" / "Public").mkdir(parents=True)
            create_proton_user(prefix, "OtherUser")
            steamuser = create_proton_user(prefix, "steamuser")

            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch("harness_utils.paths.get_proton_prefix", return_value=prefix):
                    self.assertEqual(
                        paths.windows_local_appdata(APP_ID),
                        steamuser / "AppData" / "Local",
                    )
                    self.assertEqual(
                        paths.windows_roaming_appdata(APP_ID),
                        steamuser / "AppData" / "Roaming",
                    )

    def test_proton_user_dir_falls_back_to_first_non_public_user(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp) / "pfx"
            (prefix / "drive_c" / "users" / "Public").mkdir(parents=True)
            user_dir = create_proton_user(prefix, "AlphaUser")

            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch("harness_utils.paths.get_proton_prefix", return_value=prefix):
                    self.assertEqual(paths.windows_documents(APP_ID), user_dir / "Documents")
                    self.assertEqual(
                        paths.windows_saved_games(APP_ID),
                        user_dir / "Saved Games",
                    )

    def test_missing_proton_path_raises_exact_missing_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp) / "missing-pfx"

            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch("harness_utils.paths.get_proton_prefix", return_value=prefix):
                    with self.assertRaisesRegex(RuntimeError, re.escape(f"Missing path: {prefix}")):
                        paths.windows_documents(APP_ID)


if __name__ == "__main__":
    unittest.main()
