# 📖 Perf-Dock User Guide

> A complete guide to installing, using, and troubleshooting **Perf-Dock**, the GNOME tray applet for `cpupower` CPU frequency scaling.

---

## 🚀 1. Installation

### Step 1: Install System Libraries

```bash
make install-system-deps
```

This installs GTK3/Ayatana GObject bindings, libnotify, `policykit-1` (for `pkexec`), and the `cpupower` CLI itself (`linux-tools-common`/`linux-tools-generic` on Debian/Ubuntu).

If you'd rather install manually:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-gi \
    gir1.2-gtk-3.0 \
    gir1.2-ayatanaappindicator3-0.1 \
    gir1.2-notify-0.7 \
    linux-tools-common \
    linux-tools-generic \
    policykit-1
```

### Step 2: Install Perf-Dock

**Recommended — `pipx` (system-wide, isolated):**
```bash
pipx install . --system-site-packages
make install-polkit
```

**Pythonic — active environment:**
```bash
make install
```

**Developer environment:**
```bash
make setup
```

Run `make install-polkit` once if you want Polkit to retain authorization for
several changes. The installed root-owned helper accepts only Perf-Dock's
governor and frequency-range operations; generic `pkexec` commands remain
protected. Polkit normally retains this dedicated approval for a short period
(commonly about five minutes), rather than storing your password in a keyring.

### Step 3A: Install the GNOME Shell Extension

For the minimal one-click GNOME 50 interface:

```bash
make install-extension
make enable-extension
```

The first installation may require logging out and back in before GNOME Shell
discovers the extension. GNOME on Wayland also caches extension JavaScript, so
log out and back in after installing a source update.

The extension displays every governor reported by the active CPU driver as an
alphabetically ordered icon in one panel strip. Click an icon to select that
governor. The selected icon has a high-contrast blue background and white
outline; hovering or focusing an icon shows its name and scaling behavior.

The Shell extension deliberately has no popup menu, visibility toggles,
frequency-range controls, or backend quit/restart action. Use the standalone
AppIndicator below when those richer controls are needed.

### Step 3B: Run the Standalone AppIndicator

```bash
make run
```

You should see a gauge-style icon appear in your top panel, reflecting your
current CPU governor. Clicking it opens the full tray menu described below.

---

## 🎛️ 2. Core Concepts

1.  **`cpupower`**: The Linux CLI for reading and changing CPU frequency-scaling policy — the governor (e.g. `performance`, `powersave`, `ondemand`) and the min/max frequency bounds the governor is allowed to pick within.
2.  **Governors vs. custom ranges**: Most of the time you just want a governor (a policy that auto-manages frequency). Sometimes you want to pin an explicit min/max range yourself — Perf-Dock calls this the `CUSTOM` state.
3.  **Why a tray applet?** `cpupower frequency-set` requires root and a bit of flag memorization. Perf-Dock wraps it in one click plus a password prompt, and shows you the current state at a glance without running `cpupower frequency-info` yourself.

---

## 🖱️ 3. Standalone Tray Menu Walkthrough

```
+------------------------------------------+
|  ⚡ Perf-Dock: Performance                | <-- Status header (click only if in ERROR state)
|------------------------------------------|
|  ( ) Conservative                        | <-- Governors, read from hardware at runtime
|  ( ) Ondemand                            |
|  (•) Performance                         | <-- Currently active governor is marked
|  ( ) Powersave                           |
|  ( ) Schedutil                           |
|------------------------------------------|
|  🎚️ Set Frequency Range...               | <-- Opens min/max picker dialog
|  ↩️ Restore Default Range                | <-- Only shown when in CUSTOM state
|  🔄 Refresh                              |
|------------------------------------------|
|  🚪 Quit                                 |
+------------------------------------------+
```

*   **Selecting a governor** immediately requests the scoped privileged helper to run `cpupower frequency-set -g <governor> -r`. Without the optional Polkit helper installation, Perf-Dock falls back to the standard `pkexec` password prompt. If you cancel the prompt, nothing changes and a desktop notification tells you the request was cancelled.
*   **Set Frequency Range...** opens a dialog pre-filled with your hardware's actual supported frequency steps — pick a "No change" option to leave either bound alone. Selecting a minimum greater than the maximum is rejected before anything runs.
*   **Restore Default Range** resets min/max back to your hardware's full reported range — the escape hatch back to a stock profile once you've pinned a custom range.

---

## 🔁 4. Real-Time Sync

Perf-Dock polls `cpupower frequency-info` every `--poll-interval` seconds (default 1.5s) in a background thread. If you change the governor from a terminal, another tool, or GNOME's own power settings, Perf-Dock's tray icon updates automatically within one poll cycle — no need to click Refresh.

---

## ⚙️ 5. Command-Line Options

```bash
python3 -m perf_dock.main --poll-interval 1.0 --verbose
```

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--poll-interval` | `1.5` | Background monitor polling interval, in seconds. |
| `--verbose` | off | Enable debug-level logging. |

---

## 🔍 6. Troubleshooting

### Q: The tray icon shows a warning and the menu says "cpupower not available"
`cpupower` isn't installed, or your kernel/driver doesn't expose any governors. Click the status item — it shows the install command for your distro (`apt`, `dnf`, or `pacman`). After installing, click **Refresh**.

### Q: I clicked a governor and nothing happened
You likely dismissed the `pkexec` password prompt, or entered the wrong password. Perf-Dock never applies a change on a failed/cancelled prompt — a desktop notification confirms this. Just try again.

### Q: My tray icon is missing entirely
Some GNOME Shell setups (Debian, Arch, vanilla GNOME) don't display legacy AppIndicators by default. Install the **[AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/)** GNOME Shell extension, or on Debian-based systems: `sudo apt install gnome-shell-extension-appindicator`.

### Q: I also use GNOME's built-in Power Mode setting — will they conflict?
Possibly. GNOME's `power-profiles-daemon` can override governor changes on its own schedule. Perf-Dock detects when it's active and adds a note to the tray tooltip, but does not disable or fight it in this version.

### Q: Can I run the test suite without real hardware or root?
Yes — every `cpupower`/`pkexec` call is mocked in the test suite:
```bash
make test
```
