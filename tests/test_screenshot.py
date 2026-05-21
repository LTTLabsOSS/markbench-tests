"""Tests for screenshot helpers."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from harness_utils import screenshot


class FakeMss:
    def __init__(self):
        self.output = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def shot(self, output):
        self.output = output


class ScreenshotHelperTests(unittest.TestCase):
    def test_wayland_uses_grim_when_available(self):
        result = Mock(returncode=0, stderr="")
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "screenshot.png"
            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch.dict(os.environ, {"WAYLAND_DISPLAY": "wayland-1"}):
                    with patch("harness_utils.screenshot.shutil.which", return_value="/usr/bin/grim"):
                        with patch("harness_utils.screenshot.subprocess.run", return_value=result) as run:
                            screenshot.take_screenshot_file(output_path)

        run.assert_called_once_with(
            ["/usr/bin/grim", str(output_path)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_without_grim_uses_mss_file_capture(self):
        fake_mss = FakeMss()
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "screenshot.png"
            with patch("harness_utils.platform.platform.system", return_value="Linux"):
                with patch.dict(os.environ, {}, clear=True):
                    with patch("harness_utils.screenshot.mss.mss", return_value=fake_mss):
                        screenshot.take_screenshot_file(output_path)

        self.assertEqual(fake_mss.output, str(output_path))


if __name__ == "__main__":
    unittest.main()
