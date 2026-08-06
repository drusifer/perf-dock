"""Session D-Bus service used by the GNOME Shell extension."""

import logging
import signal
from collections.abc import Callable
from pathlib import Path
from typing import Any

from perf_dock.controller import PerfDockController, StateSnapshot
from perf_dock.monitor import PerfDockMonitor
from perf_dock.ppd_check import is_ppd_active

logger = logging.getLogger("perf_dock.service")

BUS_NAME = "io.github.perf_dock"
OBJECT_PATH = "/io/github/perf_dock"
INTERFACE_NAME = "io.github.perf_dock.Control1"
INTERFACE_XML_PATH = Path(__file__).parent / "dbus" / "io.github.perf_dock.Control1.xml"


def snapshot_payload(snapshot: StateSnapshot, busy: bool = False) -> dict[str, Any]:
    """Convert internal state into a stable, null-free D-Bus payload."""
    return {
        "state": snapshot.state,
        "governor": snapshot.governor or "",
        "policy_min": snapshot.policy_min or 0,
        "policy_max": snapshot.policy_max or 0,
        "hw_min": snapshot.hw_min or 0,
        "hw_max": snapshot.hw_max or 0,
        "busy": busy,
    }


class ControlServiceCore:
    """Transport-independent implementation of the Control1 contract."""

    def __init__(
        self,
        controller: PerfDockController,
        show_range_dialog: Callable[[], None] | None = None,
        quit_callback: Callable[[], None] | None = None,
    ) -> None:
        self.controller = controller
        self.show_range_dialog = show_range_dialog
        self.quit_callback = quit_callback

    def get_snapshot(self) -> dict[str, Any]:
        """Return current state in the public contract shape."""
        payload = snapshot_payload(
            self.controller.get_details(), busy=self.controller.is_busy()
        )
        payload["ppd_active"] = is_ppd_active()
        return payload

    def get_governors(self) -> list[str]:
        """Return the governors currently exposed by the hardware."""
        return self.controller.get_governors()

    def set_governor(self, name: str) -> tuple[bool, str]:
        """Apply only a runtime-discovered governor name."""
        if name not in self.get_governors():
            return False, f"Governor '{name}' is not available"
        if self.controller.is_busy():
            return False, "Another frequency change is already in progress"
        if not self.controller.set_governor(name):
            return False, f"Could not switch to {name}: cancelled or failed"
        return True, ""

    def show_range(self) -> tuple[bool, str]:
        """Ask the graphical backend to show its existing range dialog."""
        if self.show_range_dialog is None:
            return False, "Frequency range dialog is unavailable in service mode"
        self.show_range_dialog()
        return True, ""

    def restore_default_range(self) -> tuple[bool, str]:
        """Restore hardware bounds through the existing controller."""
        if self.controller.is_busy():
            return False, "Another frequency change is already in progress"
        if not self.controller.restore_default_range():
            return False, "Could not restore the default frequency range"
        return True, ""

    def quit(self) -> None:
        """Request service shutdown if a lifecycle callback is registered."""
        if self.quit_callback:
            self.quit_callback()


class PerfDockDBusService:
    """Gio adapter exporting :class:`ControlServiceCore` on the session bus."""

    def __init__(self, poll_interval: float = 1.5) -> None:
        import gi

        gi.require_version("Gio", "2.0")
        from gi.repository import Gio, GLib

        self.Gio = Gio
        self.GLib = GLib
        self.loop = GLib.MainLoop()
        self.controller = PerfDockController()
        self.core = ControlServiceCore(
            self.controller,
            show_range_dialog=self._show_range_dialog,
            quit_callback=self.loop.quit,
        )
        self.monitor = PerfDockMonitor(
            self.controller,
            callback=self._snapshot_changed,
            poll_interval=poll_interval,
        )
        self.connection = None
        self.registration_id = 0
        xml = INTERFACE_XML_PATH.read_text(encoding="utf-8")
        self.node_info = Gio.DBusNodeInfo.new_for_xml(xml)

    def run(self) -> int:
        """Own the service name and run until Quit or a termination signal."""
        owner_id = self.Gio.bus_own_name(
            self.Gio.BusType.SESSION,
            BUS_NAME,
            self.Gio.BusNameOwnerFlags.NONE,
            self._on_bus_acquired,
            None,
            self._on_name_lost,
        )
        signal.signal(signal.SIGINT, lambda *_args: self.loop.quit())
        signal.signal(signal.SIGTERM, lambda *_args: self.loop.quit())
        self.monitor.start()
        try:
            self.loop.run()
        finally:
            self.monitor.stop()
            if self.connection and self.registration_id:
                self.connection.unregister_object(self.registration_id)
            self.Gio.bus_unown_name(owner_id)
        return 0

    def _on_bus_acquired(self, connection, _name: str) -> None:
        self.connection = connection
        interface = self.node_info.interfaces[0]
        self.registration_id = connection.register_object(
            OBJECT_PATH, interface, self._handle_method_call, None, None
        )

    def _on_name_lost(self, _connection, _name: str) -> None:
        logger.error("Could not own D-Bus name %s", BUS_NAME)
        self.loop.quit()

    def _show_range_dialog(self) -> None:
        from perf_dock.range_dialog import show_frequency_range_dialog

        show_frequency_range_dialog(self.controller)

    def _variant_dict(self, payload: dict[str, Any]) -> dict[str, Any]:
        variants = {}
        for key, value in payload.items():
            signature = (
                "b"
                if isinstance(value, bool)
                else "x"
                if isinstance(value, int)
                else "s"
            )
            variants[key] = self.GLib.Variant(signature, value)
        return variants

    def _snapshot_variant(self, payload: dict[str, Any]):
        return self.GLib.Variant("(a{sv})", (self._variant_dict(payload),))

    def _handle_method_call(
        self,
        _connection,
        _sender,
        _object_path,
        _interface_name,
        method_name,
        parameters,
        invocation,
    ) -> None:
        if method_name in {"GetSnapshot", "Refresh"}:
            invocation.return_value(self._snapshot_variant(self.core.get_snapshot()))
        elif method_name == "GetGovernors":
            invocation.return_value(
                self.GLib.Variant("(as)", (self.core.get_governors(),))
            )
        elif method_name == "SetGovernor":
            accepted, message = self.core.set_governor(parameters.unpack()[0])
            invocation.return_value(self.GLib.Variant("(bs)", (accepted, message)))
        elif method_name == "ShowRangeDialog":
            invocation.return_value(self.GLib.Variant("(bs)", self.core.show_range()))
        elif method_name == "RestoreDefaultRange":
            result = self.core.restore_default_range()
            invocation.return_value(self.GLib.Variant("(bs)", result))
        elif method_name == "Quit":
            invocation.return_value(None)
            self.core.quit()

    def _snapshot_changed(self, snapshot: StateSnapshot) -> None:
        if not self.connection:
            return
        payload = snapshot_payload(snapshot, busy=self.controller.is_busy())
        payload["ppd_active"] = is_ppd_active()
        self.connection.emit_signal(
            None,
            OBJECT_PATH,
            INTERFACE_NAME,
            "SnapshotChanged",
            self._snapshot_variant(payload),
        )


def run_service(poll_interval: float = 1.5) -> int:
    """Run the session service entry point."""
    return PerfDockDBusService(poll_interval=poll_interval).run()
