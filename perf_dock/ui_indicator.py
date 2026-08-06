"""Perf-Dock Ayatana AppIndicator System Tray Interface."""

import logging
import os

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
try:
    gi.require_version("Notify", "0.7")
    from gi.repository import Notify

    HAS_NOTIFY = True
except (ValueError, ImportError):
    HAS_NOTIFY = False

from gi.repository import AyatanaAppIndicator3, GLib, Gtk

from perf_dock.controller import PerfDockController, StateSnapshot
from perf_dock.monitor import PerfDockMonitor
from perf_dock.ppd_check import is_ppd_active
from perf_dock.state import (
    STATE_BALANCED,
    STATE_CUSTOM,
    STATE_ERROR,
    STATE_PERFORMANCE,
    STATE_POWERSAVE,
)

logger = logging.getLogger("perf_dock.ui_indicator")

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")

_ICON_BY_STATE = {
    STATE_PERFORMANCE: "perf-dock-performance",
    STATE_POWERSAVE: "perf-dock-powersave",
    STATE_BALANCED: "perf-dock-balanced",
    STATE_CUSTOM: "perf-dock-custom",
    STATE_ERROR: "perf-dock-error",
}

_LABEL_BY_STATE = {
    STATE_PERFORMANCE: "Perf-Dock: Performance",
    STATE_POWERSAVE: "Perf-Dock: Power Saver",
    STATE_BALANCED: "Perf-Dock: Balanced",
    STATE_CUSTOM: "Perf-Dock: Custom",
    STATE_ERROR: "Perf-Dock: cpupower not available",
}

INSTALL_HINT = (
    "cpupower was not found on this system.\n"
    "Debian/Ubuntu: sudo apt install linux-tools-common linux-tools-generic\n"
    "Fedora: sudo dnf install kernel-tools\n"
    "Arch: sudo pacman -S cpupower"
)


def _format_freq(khz: int) -> str:
    """Formats a kHz value as a short human string, e.g. '800MHz' or '2.4GHz'."""
    mhz = khz / 1000
    if mhz >= 1000:
        return f"{mhz / 1000:.1f}GHz"
    return f"{mhz:.0f}MHz"


class PerfDockIndicator:
    """System tray indicator (Ayatana AppIndicator) for cpupower frequency scaling."""

    def __init__(
        self,
        controller: PerfDockController,
        monitor: PerfDockMonitor,
    ) -> None:
        self.controller: PerfDockController = controller
        self.monitor: PerfDockMonitor = monitor
        self._governor_items: dict[str, Gtk.RadioMenuItem] = {}
        self._updating_governor_selection = False

        logger.info("Initializing Ayatana AppIndicator with icon path: %s", ICONS_DIR)

        self._init_notifications()

        self.indicator = AyatanaAppIndicator3.Indicator.new_with_path(
            "perf-dock",
            "perf-dock-balanced",
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
            ICONS_DIR,
        )
        self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("Perf-Dock")

        self.menu = Gtk.Menu()
        self._build_menu()
        self.indicator.set_menu(self.menu)

        self.monitor._callback = self._on_state_changed

        self.update_ui(self.controller.get_details())

    def _init_notifications(self) -> None:
        global HAS_NOTIFY
        if HAS_NOTIFY:
            try:
                Notify.init("Perf-Dock")
                logger.info("Desktop notifications initialized.")
            except Exception as e:
                HAS_NOTIFY = False
                logger.warning("Failed to initialize desktop notifications: %s", e)

    def _send_notification(self, title: str, message: str) -> None:
        if HAS_NOTIFY:
            try:
                n = Notify.Notification.new(title, message, "cpu")
                n.show()
            except Exception as e:
                logger.warning("Failed to show desktop notification: %s", e)

    def _build_menu(self) -> None:
        """Builds all menu items for the tray context menu."""
        self.menu_status = Gtk.MenuItem(label="Perf-Dock: Unknown")
        self.menu_status.set_sensitive(False)
        self.menu_status.connect("activate", self._on_error_status_clicked)
        self.menu.append(self.menu_status)

        self.menu.append(Gtk.SeparatorMenuItem())

        group = None
        for name in self.controller.get_governors():
            item = Gtk.RadioMenuItem.new_with_label(group, name.capitalize())
            if group is None:
                group = item.get_group()
            item.connect("toggled", self._on_governor_toggled, name)
            self.menu.append(item)
            self._governor_items[name] = item

        self.menu.append(Gtk.SeparatorMenuItem())

        self.menu_range = Gtk.MenuItem(label="Set Frequency Range...")
        self.menu_range.connect("activate", self._on_range_clicked)
        self.menu.append(self.menu_range)

        self.menu_restore = Gtk.MenuItem(label="Restore Default Range")
        self.menu_restore.connect("activate", self._on_restore_clicked)
        self.menu.append(self.menu_restore)

        self.menu_refresh = Gtk.MenuItem(label="Refresh")
        self.menu_refresh.connect("activate", self._on_refresh_clicked)
        self.menu.append(self.menu_refresh)

        self.menu.append(Gtk.SeparatorMenuItem())

        menu_quit = Gtk.MenuItem(label="Quit")
        menu_quit.connect("activate", self._on_quit_clicked)
        self.menu.append(menu_quit)

        self.menu.show_all()

    def update_ui(self, snapshot: StateSnapshot) -> None:
        """Updates the tray icon, tooltip, and menu item state from a StateSnapshot."""
        state = snapshot.state
        logger.debug("Updating UI to state: %s", state)

        icon_name = _ICON_BY_STATE.get(state, "perf-dock-error")
        label = _LABEL_BY_STATE.get(state, "Perf-Dock: Unknown")
        if state == STATE_BALANCED and snapshot.governor:
            label = f"{label} ({snapshot.governor})"
        elif (
            state == STATE_CUSTOM
            and snapshot.policy_min is not None
            and snapshot.policy_max is not None
        ):
            label = (
                f"Perf-Dock: Custom {_format_freq(snapshot.policy_min)}"
                f"-{_format_freq(snapshot.policy_max)}"
            )
        if is_ppd_active():
            label += " — Note: power-profiles-daemon is also active"

        self.indicator.set_icon_full(icon_name, label)
        self.indicator.set_title(label)
        self.menu_status.set_label(label)
        self.menu_status.set_sensitive(state == STATE_ERROR)

        is_error = state == STATE_ERROR
        for name, item in self._governor_items.items():
            item.set_visible(not is_error)
            self._updating_governor_selection = True
            item.set_active(not is_error and name == snapshot.governor)
            self._updating_governor_selection = False

        self.menu_range.set_visible(not is_error)
        self.menu_restore.set_visible(not is_error and state == STATE_CUSTOM)

    def _on_state_changed(self, snapshot: StateSnapshot) -> None:
        """Callback from PerfDockMonitor. Runs on the main thread via GLib.idle_add."""
        GLib.idle_add(self.update_ui, snapshot)

    def _on_governor_toggled(self, widget: Gtk.RadioMenuItem, name: str) -> None:
        if self._updating_governor_selection or not widget.get_active():
            return
        if self.controller.is_busy():
            # A pkexec prompt from another menu action is already in flight
            # (possible via GTK's nested dialog main loop) — ignore this click
            # rather than double-submitting a privileged call.
            return
        logger.info("User selected governor: %s", name)
        if not self.controller.set_governor(name):
            self._send_notification(
                "Perf-Dock",
                f"Could not switch to {name}: the request was cancelled or failed.",
            )
        self.update_ui(self.controller.get_details())

    def _on_range_clicked(self, _widget: Gtk.MenuItem) -> None:
        if self.controller.is_busy():
            return
        self.show_range_dialog()

    def show_range_dialog(self) -> None:
        """Opens the frequency-range dialog, pre-filled from hardware steps/policy."""
        from perf_dock.range_dialog import show_frequency_range_dialog

        show_frequency_range_dialog(
            self.controller,
            notify=lambda message: self._send_notification("Perf-Dock", message),
        )
        self.update_ui(self.controller.get_details())

    def _on_restore_clicked(self, _widget: Gtk.MenuItem) -> None:
        if self.controller.is_busy():
            return
        logger.info("User clicked: Restore Default Range")
        if not self.controller.restore_default_range():
            self._send_notification(
                "Perf-Dock",
                "Could not restore default range: the request was cancelled or failed.",
            )
        self.update_ui(self.controller.get_details())

    def _on_refresh_clicked(self, _widget: Gtk.MenuItem) -> None:
        self.update_ui(self.controller.get_details())

    def _on_error_status_clicked(self, _widget: Gtk.MenuItem) -> None:
        self._send_notification("Perf-Dock", INSTALL_HINT)

    def _on_quit_clicked(self, _widget: Gtk.MenuItem) -> None:
        logger.info("User clicked: Quit Application")
        self.shutdown()
        Gtk.main_quit()

    def shutdown(self) -> None:
        """Stops the background monitor and tears down notifications cleanly."""
        logger.info("Shutting down Perf-Dock Indicator...")
        self.monitor.stop()
        if HAS_NOTIFY:
            try:
                Notify.uninit()
            except Exception as e:
                logger.warning("Error during notification shutdown: %s", e)
