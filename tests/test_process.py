"""Tests for process helpers."""

import unittest
from unittest.mock import patch

from harness_utils import process


class FakeProcess:
    def __init__(self, pid: int, name: str):
        self.pid = pid
        self.info = {"pid": pid, "name": name}
        self.terminated = False

    def name(self):
        return self.info["name"]

    def terminate(self):
        self.terminated = True


class ProcessHelperTests(unittest.TestCase):
    def test_is_process_running_normalizes_case_and_prefers_exact_match(self):
        exact = FakeProcess(1, "Cyberpunk2077.exe")
        substring = FakeProcess(2, "Cyberpunk2077Launcher.exe")

        with patch("harness_utils.process.psutil.process_iter", return_value=[substring, exact]):
            result = process.is_process_running("cyberpunk2077.EXE")

        self.assertIs(result, exact)

    def test_is_process_running_uses_substring_fallback(self):
        substring = FakeProcess(2, "Cyberpunk2077Launcher.exe")

        with patch("harness_utils.process.psutil.process_iter", return_value=[substring]):
            result = process.is_process_running("cyberpunk2077.exe")

        self.assertIs(result, substring)

    def test_terminate_processes_logs_and_terminates_matches_once(self):
        exact = FakeProcess(1, "Cyberpunk2077.exe")

        with patch("harness_utils.process.psutil.process_iter", return_value=[exact]):
            with self.assertLogs("harness_utils.process", level="INFO") as logs:
                process.terminate_processes("Cyberpunk2077.exe", "cyberpunk2077")

        self.assertTrue(exact.terminated)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("pid=1", logs.output[0])
        self.assertIn("Cyberpunk2077.exe", logs.output[0])


if __name__ == "__main__":
    unittest.main()
