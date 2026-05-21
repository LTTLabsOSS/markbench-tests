"""Tests for platform helpers."""

import unittest
from unittest.mock import patch

from harness_utils import platform


class PlatformHelperTests(unittest.TestCase):
    def test_platform_booleans_use_platform_system(self):
        with patch("harness_utils.platform.platform.system", return_value="Windows"):
            self.assertTrue(platform.is_windows())
            self.assertFalse(platform.is_linux())

        with patch("harness_utils.platform.platform.system", return_value="Linux"):
            self.assertTrue(platform.is_linux())
            self.assertFalse(platform.is_windows())

    def test_require_helpers_raise_on_wrong_platform(self):
        with patch("harness_utils.platform.platform.system", return_value="Linux"):
            with self.assertRaisesRegex(RuntimeError, "requires Windows"):
                platform.require_windows("feature")

        with patch("harness_utils.platform.platform.system", return_value="Windows"):
            with self.assertRaisesRegex(RuntimeError, "requires Linux"):
                platform.require_linux("feature")


if __name__ == "__main__":
    unittest.main()
