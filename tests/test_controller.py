"""Unit tests for perf_dock.controller — all subprocess/cpufreq calls are mocked."""

import unittest
from unittest.mock import MagicMock, patch

from perf_dock import cpufreq
from perf_dock.controller import PerfDockController
from perf_dock.state import STATE_CUSTOM, STATE_ERROR, STATE_PERFORMANCE


class TestPerfDockController(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = PerfDockController()

    @patch("perf_dock.controller.cpufreq.is_available", return_value=True)
    def test_is_available_passthrough(self, _mock: patch) -> None:
        self.assertTrue(self.controller.is_available())

    def test_is_busy_false_by_default(self) -> None:
        self.assertFalse(self.controller.is_busy())

    @patch("perf_dock.controller.cpufreq.get_hwlimits", return_value=(710400, 3417600))
    @patch(
        "perf_dock.controller.cpufreq.get_policy",
        return_value=("performance", 710400, 3417600),
    )
    def test_get_details_performance(
        self, _mock_policy: patch, _mock_hw: patch
    ) -> None:
        snapshot = self.controller.get_details()
        self.assertEqual(snapshot.state, STATE_PERFORMANCE)
        self.assertEqual(snapshot.governor, "performance")

    @patch("perf_dock.controller.cpufreq.get_hwlimits", return_value=(710400, 3417600))
    @patch(
        "perf_dock.controller.cpufreq.get_policy",
        return_value=("ondemand", 1000000, 2000000),
    )
    def test_get_details_custom_range(
        self, _mock_policy: patch, _mock_hw: patch
    ) -> None:
        snapshot = self.controller.get_details()
        self.assertEqual(snapshot.state, STATE_CUSTOM)

    @patch(
        "perf_dock.controller.cpufreq.get_policy",
        side_effect=cpufreq.CpuFreqUnavailableError("no cpupower"),
    )
    def test_get_details_error_when_cpupower_unavailable(
        self, _mock_policy: patch
    ) -> None:
        snapshot = self.controller.get_details()
        self.assertEqual(snapshot.state, STATE_ERROR)

    @patch(
        "perf_dock.controller.cpufreq.get_governors",
        return_value=["ondemand", "performance"],
    )
    def test_get_governors_passthrough(self, _mock: patch) -> None:
        self.assertEqual(self.controller.get_governors(), ["ondemand", "performance"])

    @patch(
        "perf_dock.controller.cpufreq.get_governors",
        side_effect=cpufreq.CpuFreqUnavailableError("missing"),
    )
    def test_get_governors_empty_on_error(self, _mock: patch) -> None:
        self.assertEqual(self.controller.get_governors(), [])

    @patch("perf_dock.controller.subprocess.run")
    @patch(
        "perf_dock.controller.cpufreq.get_cpupower_path",
        return_value="/usr/bin/cpupower",
    )
    def test_set_governor_success(self, _mock_path: patch, mock_run: patch) -> None:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = self.controller.set_governor("performance")
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["pkexec", "/usr/bin/cpupower", "frequency-set", "-r", "-g", "performance"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertFalse(self.controller.is_busy())

    @patch("perf_dock.controller.subprocess.run")
    @patch(
        "perf_dock.controller.cpufreq.get_cpupower_path",
        return_value="/usr/bin/cpupower",
    )
    def test_set_governor_cancelled_prompt_returns_false(
        self, _mock_path: patch, mock_run: patch
    ) -> None:
        mock_run.return_value = MagicMock(returncode=127, stderr="Request dismissed\n")
        result = self.controller.set_governor("performance")
        self.assertFalse(result)
        self.assertFalse(self.controller.is_busy())

    @patch("perf_dock.controller.subprocess.run")
    @patch(
        "perf_dock.controller.cpufreq.get_cpupower_path",
        return_value="/usr/bin/cpupower",
    )
    def test_set_range_both_bounds(self, _mock_path: patch, mock_run: patch) -> None:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = self.controller.set_range(1000000, 2000000)
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            [
                "pkexec",
                "/usr/bin/cpupower",
                "frequency-set",
                "-r",
                "-d",
                "1000000kHz",
                "-u",
                "2000000kHz",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("perf_dock.controller.subprocess.run")
    @patch(
        "perf_dock.controller.cpufreq.get_cpupower_path",
        return_value="/usr/bin/cpupower",
    )
    def test_set_range_min_only(self, _mock_path: patch, mock_run: patch) -> None:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        self.controller.set_range(1000000, None)
        mock_run.assert_called_once_with(
            ["pkexec", "/usr/bin/cpupower", "frequency-set", "-r", "-d", "1000000kHz"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_set_range_no_bounds_is_noop(self) -> None:
        result = self.controller.set_range(None, None)
        self.assertTrue(result)

    @patch("perf_dock.controller.subprocess.run")
    @patch(
        "perf_dock.controller.cpufreq.get_cpupower_path",
        return_value="/usr/bin/cpupower",
    )
    @patch("perf_dock.controller.cpufreq.get_hwlimits", return_value=(710400, 3417600))
    def test_restore_default_range(
        self, _mock_hw: patch, _mock_path: patch, mock_run: patch
    ) -> None:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = self.controller.restore_default_range()
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            [
                "pkexec",
                "/usr/bin/cpupower",
                "frequency-set",
                "-r",
                "-d",
                "710400kHz",
                "-u",
                "3417600kHz",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch(
        "perf_dock.controller.cpufreq.get_cpupower_path",
        side_effect=cpufreq.CpuFreqUnavailableError("missing"),
    )
    def test_set_governor_returns_false_when_cpupower_missing(
        self, _mock_path: patch
    ) -> None:
        result = self.controller.set_governor("performance")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
