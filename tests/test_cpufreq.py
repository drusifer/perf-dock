"""Unit tests for perf_dock.cpufreq — parsing is mocked, never touches real hardware."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from perf_dock import cpufreq


def _completed(stdout: str) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    result.returncode = 0
    return result


class TestCpuFreq(unittest.TestCase):
    def setUp(self) -> None:
        # Reset the module-level cached path between tests.
        cpufreq._CPUPOWER_PATH = None

    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_is_available_true(self, _mock_which: patch) -> None:
        self.assertTrue(cpufreq.is_available())

    @patch("perf_dock.cpufreq.shutil.which", return_value=None)
    def test_is_available_false(self, _mock_which: patch) -> None:
        self.assertFalse(cpufreq.is_available())

    @patch("perf_dock.cpufreq.shutil.which", return_value=None)
    def test_get_governors_raises_when_missing(self, _mock_which: patch) -> None:
        with self.assertRaises(cpufreq.CpuFreqUnavailableError):
            cpufreq.get_governors()

    @patch("perf_dock.cpufreq.subprocess.run")
    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_get_governors(self, _mock_which: patch, mock_run: patch) -> None:
        mock_run.return_value = _completed(
            "analyzing CPU 8:\n"
            "  available cpufreq governors: conservative ondemand userspace "
            "powersave performance schedutil\n"
        )
        governors = cpufreq.get_governors()
        self.assertEqual(
            governors,
            [
                "conservative",
                "ondemand",
                "userspace",
                "powersave",
                "performance",
                "schedutil",
            ],
        )
        mock_run.assert_called_once_with(
            ["/usr/bin/cpupower", "frequency-info", "-g"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("perf_dock.cpufreq.subprocess.run")
    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_get_hwlimits(self, _mock_which: patch, mock_run: patch) -> None:
        mock_run.return_value = _completed("analyzing CPU 8:\n710400 3417600\n")
        hw_min, hw_max = cpufreq.get_hwlimits()
        self.assertEqual((hw_min, hw_max), (710400, 3417600))

    @patch("perf_dock.cpufreq.subprocess.run")
    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_get_policy(self, _mock_which: patch, mock_run: patch) -> None:
        mock_run.return_value = _completed(
            "analyzing CPU 2:\n"
            "  current policy: frequency should be within 710 MHz and 3.42 GHz.\n"
            '                  The governor "performance" may decide which speed\n'
            "                  to use within this range.\n"
        )
        governor, policy_min, policy_max = cpufreq.get_policy()
        self.assertEqual(governor, "performance")
        self.assertEqual(policy_min, 710000)
        self.assertEqual(policy_max, 3420000)

    @patch("perf_dock.cpufreq.subprocess.run")
    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_get_frequency_steps(self, _mock_which: patch, mock_run: patch) -> None:
        mock_run.return_value = _completed(
            "  available frequency steps:  710 MHz, 806 MHz, 998 MHz, 1.19 GHz, "
            "1.44 GHz, 1.67 GHz, 1.92 GHz, 2.19 GHz, 2.52 GHz, 2.71 GHz, 2.98 GHz, "
            "3.21 GHz, 3.42 GHz\n"
        )
        steps = cpufreq.get_frequency_steps()
        self.assertEqual(steps[0], 710000)
        self.assertEqual(steps[-1], 3420000)
        self.assertEqual(steps, sorted(steps))
        mock_run.assert_called_once_with(
            ["/usr/bin/cpupower", "frequency-info"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("perf_dock.cpufreq.subprocess.run")
    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_get_policy_unparseable_output_raises(
        self, _mock_which: patch, mock_run: patch
    ) -> None:
        mock_run.return_value = _completed("garbage output\n")
        with self.assertRaises(cpufreq.CpuFreqUnavailableError):
            cpufreq.get_policy()

    @patch("perf_dock.cpufreq.subprocess.run")
    @patch("perf_dock.cpufreq.shutil.which", return_value="/usr/bin/cpupower")
    def test_get_governors_subprocess_failure_raises(
        self, _mock_which: patch, mock_run: patch
    ) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "cpupower")
        with self.assertRaises(cpufreq.CpuFreqUnavailableError):
            cpufreq.get_governors()


if __name__ == "__main__":
    unittest.main()
