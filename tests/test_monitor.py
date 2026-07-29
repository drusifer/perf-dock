"""Unit tests for perf_dock.monitor — GLib dispatch is patched out for determinism."""

import time
import unittest
from unittest.mock import MagicMock, patch

from perf_dock.controller import PerfDockController, StateSnapshot
from perf_dock.monitor import PerfDockMonitor
from perf_dock.state import STATE_BALANCED, STATE_PERFORMANCE


class TestPerfDockMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = MagicMock(spec=PerfDockController)
        self.callback = MagicMock()
        self.monitor = PerfDockMonitor(
            controller=self.controller,
            callback=self.callback,
            poll_interval=0.01,
        )

    @patch("perf_dock.monitor.HAS_GLIB", False)
    def test_poll_once_dispatches_on_first_read(self) -> None:
        snapshot = StateSnapshot(state=STATE_BALANCED, governor="ondemand")
        self.controller.get_details.return_value = snapshot

        result = self.monitor.poll_once()

        self.assertEqual(result, snapshot)
        self.callback.assert_called_once_with(snapshot)

    @patch("perf_dock.monitor.HAS_GLIB", False)
    def test_poll_once_does_not_redispatch_unchanged_state(self) -> None:
        snapshot = StateSnapshot(state=STATE_BALANCED, governor="ondemand")
        self.controller.get_details.return_value = snapshot

        self.monitor.poll_once()
        self.monitor.poll_once()

        self.callback.assert_called_once_with(snapshot)

    @patch("perf_dock.monitor.HAS_GLIB", False)
    def test_poll_once_redispatches_on_change(self) -> None:
        first = StateSnapshot(state=STATE_BALANCED, governor="ondemand")
        second = StateSnapshot(state=STATE_PERFORMANCE, governor="performance")
        self.controller.get_details.side_effect = [first, second]

        self.monitor.poll_once()
        self.monitor.poll_once()

        self.assertEqual(self.callback.call_count, 2)
        self.callback.assert_called_with(second)

    @patch("perf_dock.monitor.HAS_GLIB", True)
    @patch("perf_dock.monitor.GLib")
    def test_poll_once_uses_glib_idle_add_when_available(
        self, mock_glib: MagicMock
    ) -> None:
        snapshot = StateSnapshot(state=STATE_BALANCED, governor="ondemand")
        self.controller.get_details.return_value = snapshot

        self.monitor.poll_once()

        mock_glib.idle_add.assert_called_once_with(self.callback, snapshot)

    def test_start_stop_lifecycle(self) -> None:
        self.controller.get_details.return_value = StateSnapshot(state=STATE_BALANCED)

        self.monitor.start()
        self.assertTrue(self.monitor._active)
        time.sleep(0.03)
        self.monitor.stop()

        self.assertFalse(self.monitor._active)
        self.assertGreaterEqual(self.controller.get_details.call_count, 1)

    def test_start_is_idempotent(self) -> None:
        self.controller.get_details.return_value = StateSnapshot(state=STATE_BALANCED)
        self.monitor.start()
        first_thread = self.monitor._thread
        self.monitor.start()
        self.assertIs(self.monitor._thread, first_thread)
        self.monitor.stop()


if __name__ == "__main__":
    unittest.main()
