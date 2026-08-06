"""Shared GTK frequency-range dialog for indicator and D-Bus service modes."""

from collections.abc import Callable

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from perf_dock.controller import PerfDockController


def _frequency_combo(steps: list[int], current_khz: int | None) -> Gtk.ComboBoxText:
    combo = Gtk.ComboBoxText()
    combo.append_text("No change")
    active_index = 0
    for index, step in enumerate(steps, start=1):
        combo.append_text(f"{step / 1000:.0f} MHz")
        if step == current_khz:
            active_index = index
    combo.set_active(active_index)
    return combo


def _selected_frequency(combo: Gtk.ComboBoxText, steps: list[int]) -> int | None:
    index = combo.get_active()
    return None if index <= 0 else steps[index - 1]


def _show_error(parent: Gtk.Dialog, message: str) -> None:
    error = Gtk.MessageDialog(
        transient_for=parent,
        modal=True,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=message,
    )
    error.run()
    error.destroy()


def show_frequency_range_dialog(
    controller: PerfDockController,
    notify: Callable[[str], None] | None = None,
) -> bool:
    """Show the existing range workflow and return whether a change was applied."""
    snapshot = controller.get_details()
    steps = controller.get_frequency_steps()
    dialog = Gtk.Dialog(title="Set Frequency Range", flags=Gtk.DialogFlags.MODAL)
    dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
    dialog.add_button("Apply", Gtk.ResponseType.OK)
    box = dialog.get_content_area()
    box.add(Gtk.Label(label="Minimum frequency:"))
    min_combo = _frequency_combo(steps, snapshot.policy_min)
    box.add(min_combo)
    box.add(Gtk.Label(label="Maximum frequency:"))
    max_combo = _frequency_combo(steps, snapshot.policy_max)
    box.add(max_combo)
    dialog.show_all()

    applied = False
    while True:
        response = dialog.run()
        if response != Gtk.ResponseType.OK:
            break
        min_khz = _selected_frequency(min_combo, steps)
        max_khz = _selected_frequency(max_combo, steps)
        if min_khz is not None and max_khz is not None and min_khz > max_khz:
            _show_error(
                dialog, "Minimum frequency cannot be greater than maximum frequency."
            )
            continue
        applied = controller.set_range(min_khz, max_khz)
        if not applied and notify:
            notify("Could not set frequency range: cancelled or failed.")
        break
    dialog.destroy()
    return applied
