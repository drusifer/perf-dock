# User Stories — Perf-Dock

**Author:** Cypher (Product Manager)
**Date:** 2026-07-29

---

### **US-1: System Tray Indicator & Governor Quick-Switch Menu**
*As a desktop user, I want a visible tray icon showing my current CPU performance profile, so that I can tell at a glance whether my machine is set to performance, power-saving, or balanced mode.*

- **Acceptance Criteria:**
  - An Ayatana AppIndicator icon is instantiated in the GNOME top panel.
  - The icon and tooltip update to reflect the current governor:
    - `performance` → "hot" icon, tooltip "Perf-Dock: Performance".
    - `powersave` → "cool" icon, tooltip "Perf-Dock: Power Saver".
    - `ondemand`/`schedutil`/`conservative` → neutral icon, tooltip "Perf-Dock: Balanced (<governor>)".
    - Custom pinned min/max range → distinct icon, tooltip shows the active range (e.g. "Perf-Dock: Custom 800MHz–2.4GHz").
  - Clicking the tray icon opens a dropdown menu listing every governor the hardware/driver actually supports (read from `cpupower frequency-info --governors`), not a hardcoded list.
  - Selecting a governor invokes `cpupower frequency-set -g <governor>` (with privilege escalation) and immediately reflects the new state.
  - The currently active governor is visibly checked/highlighted in the menu.
  - A **"Restore Default Range"** menu item is visible whenever the current state is `CUSTOM`; selecting it resets min/max back to the hardware's full reported limits (`--hwlimits`). This is the escape hatch back to a stock profile once a custom range has been applied (Nielsen #3: User Control and Freedom).
  - If `cpupower` is missing or the running kernel/driver reports no usable governors, the tray shows the `UNKNOWN/ERROR` icon and the menu's only enabled item is **"Perf-Dock: cpupower not available"**, which on click shows a notification with the install command for the current distro family (Nielsen #9: Help Users Recognize, Diagnose, and Recover from Errors). It does not fail silently or show an empty/dead menu.

---

### **US-2: Frequency Range Control Dialog**
*As a power user, I want to set a custom min/max CPU frequency, so that I can fine-tune performance vs. thermal/battery tradeoffs beyond the stock governor presets.*

- **Acceptance Criteria:**
  - A "Set Frequency Range..." menu item opens a dialog pre-filled with the hardware's allowed min/max (`cpupower frequency-info --hwlimits`).
  - The dialog lets the user pick min and max frequency from the hardware's available frequency steps (`cpupower frequency-info` step list), not free-text entry of arbitrary values.
  - Min and max can each be left at "no change" independently — setting only one bound is allowed (matches `cpupower frequency-set` accepting `-d` or `-u` alone; the dialog must not force both fields).
  - Confirming applies `cpupower frequency-set` with whichever of `-d <min>` / `-u <max>` the user actually changed (with privilege escalation) to all related CPUs.
  - Invalid ranges (min > max, out of hardware bounds) are rejected in the dialog before any command is run.
  - After applying, the tray transitions to the `CUSTOM` state described in US-1.

---

### **US-3: Real-Time External Change Sync**
*As a user who might also change CPU settings via terminal or another power-management tool, I want Perf-Dock to notice and reflect those changes automatically, so my tray indicator is never showing stale information.*

- **Acceptance Criteria:**
  - A background monitor loop polls `cpupower frequency-info` on a fixed interval (default 1–2s, configurable via CLI flag, mirroring nerd-dock's `--poll-interval`).
  - Any change in governor or min/max frequency detected between polls updates the tray icon/tooltip/menu state within one polling cycle.
  - UI updates happen thread-safely via `GLib.idle_add`, never blocking or racing the GTK main loop.

---

### **US-4: Safe Privilege Escalation for Mutating Commands**
*As a security-conscious user, I want Perf-Dock to only request elevated privileges at the moment a change is made, so that the applet never runs with standing root access.*

- **Acceptance Criteria:**
  - All read-only operations (`frequency-info`) run unprivileged.
  - All mutating operations (`frequency-set`) go through a single, explicit, auditable escalation path (e.g. `pkexec` with a scoped policy action) decided by Morpheus during architecture.
  - No password or credential is cached, stored, or held in memory beyond the single privileged call.
  - A failed or cancelled privilege prompt leaves the tray state unchanged and surfaces a clear error/notification rather than silently failing.

---

### **US-5: Dev Automation & Lint Suite (parity with nerd-dock)**
*As a developer, I want the same linting/static-analysis build targets used in nerd-dock, so Perf-Dock meets the same quality bar and is familiar to maintain.*

- **Acceptance Criteria:**
  - `Makefile.prj` provides a `make lint` target running `ruff check`/`ruff format`, `radon cc`, `vulture`, `bandit`, and `pylint --enable=duplicate-code`.
  - `bandit` scrutiny is explicitly applied to the subprocess/privilege-escalation code paths (US-4).
  - `make test` runs a headless unit test suite that mocks all `subprocess` calls to `cpupower` and any privilege-escalation wrapper — no real hardware or root access required in CI.
  - `make e2e` boots the real application for a few seconds against real `cpupower`/GTK and verifies clean startup (correct initial state, no traceback) and clean shutdown; it skips gracefully when no display session is available (e.g. headless CI) rather than failing.
