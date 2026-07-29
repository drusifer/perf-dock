"""Perf-Dock background poll thread, mirroring nerd-dock's monitor pattern."""

import logging
import threading
import time
from collections.abc import Callable

try:
    from gi.repository import GLib

    HAS_GLIB = True
except ImportError:
    HAS_GLIB = False

from perf_dock.controller import PerfDockController, StateSnapshot

logger = logging.getLogger("perf_dock.monitor")


class PerfDockMonitor:
    """Polls PerfDockController on a fixed interval and dispatches state changes."""

    def __init__(
        self,
        controller: PerfDockController,
        callback: Callable[[StateSnapshot], None] | None = None,
        poll_interval: float = 1.5,
    ) -> None:
        self._controller: PerfDockController = controller
        self._callback: Callable[[StateSnapshot], None] | None = callback
        self.poll_interval: float = poll_interval
        self._active: bool = False
        self._thread: threading.Thread | None = None
        self._last_snapshot: StateSnapshot | None = None

    def start(self) -> None:
        """Starts the background monitor thread."""
        if self._active:
            return
        self._active = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Monitor thread started.")

    def stop(self) -> None:
        """Stops the background monitor thread."""
        if not self._active:
            return
        self._active = False
        if self._thread:
            self._thread.join(timeout=1.0)
        logger.info("Monitor thread stopped.")

    def poll_once(self) -> StateSnapshot:
        """Reads current state; dispatches the callback only if it changed."""
        snapshot = self._controller.get_details()
        if snapshot != self._last_snapshot:
            self._last_snapshot = snapshot
            if self._callback:
                self._trigger_callback(snapshot)
        return snapshot

    def _trigger_callback(self, snapshot: StateSnapshot) -> None:
        if HAS_GLIB:
            GLib.idle_add(self._callback, snapshot)
        else:
            self._callback(snapshot)

    def _run(self) -> None:
        while self._active:
            try:
                self.poll_once()
            except Exception:
                logger.exception("Error in monitor thread")
            time.sleep(self.poll_interval)
