"""Tests for input adapter."""

import unittest
from unittest.mock import call, patch

from harness_utils.input import InputController


class InputControllerTests(unittest.TestCase):
    def test_linux_press_uses_ydotool_key_mapping(self):
        controller = InputController()

        with patch("harness_utils.platform.platform.system", return_value="Linux"):
            with patch("harness_utils.input.shutil.which", return_value="/usr/bin/ydotool"):
                with patch("harness_utils.input.subprocess.run") as run:
                    controller.press("left")

        run.assert_has_calls(
            [
                call(["/usr/bin/ydotool", "key", "105:1"], check=True),
                call(["/usr/bin/ydotool", "key", "105:0"], check=True),
            ]
        )

    def test_linux_hotkey_releases_in_reverse_order(self):
        controller = InputController()

        with patch("harness_utils.platform.platform.system", return_value="Linux"):
            with patch("harness_utils.input.shutil.which", return_value="/usr/bin/ydotool"):
                with patch("harness_utils.input.subprocess.run") as run:
                    controller.hotkey("b", "3")

        run.assert_has_calls(
            [
                call(["/usr/bin/ydotool", "key", "48:1"], check=True),
                call(["/usr/bin/ydotool", "key", "4:1"], check=True),
                call(["/usr/bin/ydotool", "key", "4:0"], check=True),
                call(["/usr/bin/ydotool", "key", "48:0"], check=True),
            ]
        )

    def test_missing_ydotool_raises_clear_error(self):
        controller = InputController()

        with patch("harness_utils.platform.platform.system", return_value="Linux"):
            with patch("harness_utils.input.shutil.which", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "ydotool"):
                    controller.press("left")


if __name__ == "__main__":
    unittest.main()
