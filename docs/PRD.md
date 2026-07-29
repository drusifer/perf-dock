# Product Requirements Document (PRD) — Perf-Dock

**Author:** Cypher (Product Manager)
**Date:** 2026-07-29
**Status:** Draft — Pending Smith (Gate 1) Review

---

## 1. Product Vision
**Perf-Dock** is a lightweight, system-wide GNOME top-bar tray applet that wraps `cpupower frequency-set` / `cpupower frequency-info`, giving users instant, visible control over CPU frequency scaling (governor and min/max clock limits) without opening a terminal. It follows the same dock-resident interaction model as its sibling project **nerd-dock** (`../nerd-dock`), which is used here as the template for architecture, tray behavior, dev tooling, and documentation structure.

---

## 2. Key Objectives
- **Zero-Overhead Governor Control:** Switch CPU governor (e.g. `performance`, `powersave`, `ondemand`, `schedutil`) directly from the GNOME top bar in one click.
- **Visible Performance State:** A dynamic tray icon and tooltip make the *current* governor/profile obvious at a glance — no need to run `cpupower frequency-info` manually.
- **Frequency Range Control:** Let advanced users set min/max CPU frequency limits (`cpupower frequency-set -d/-u`) through a simple dialog, without hand-typing frequency strings.
- **Real-Time Sync:** If the governor or frequency limits change outside Perf-Dock (CLI, another tool, a power-profile switch), the tray reflects it within one polling cycle.
- **Safe Privilege Handling:** `cpupower frequency-set` requires elevated privileges on most distros; Perf-Dock must request escalation transparently and safely (no stored passwords, no persistent root process).

---

## 3. Core Features & Specifications

### 3.1. Decorated System Tray Applet (Ayatana AppIndicator)
- Native GNOME top-bar integration, matching nerd-dock's `NerdDockIndicator` pattern.
- **Status-Driven Tray Icon & Tooltip:**
  - `PERFORMANCE`: solid/"hot" icon. Tooltip: "Perf-Dock: Performance (governor=performance)".
  - `POWERSAVE`: dim/"cool" icon. Tooltip: "Perf-Dock: Power Saver (governor=powersave)".
  - `BALANCED` (ondemand/schedutil/conservative): neutral icon. Tooltip: "Perf-Dock: Balanced (governor=<name>)".
  - `CUSTOM`: distinct icon when min/max frequency has been manually pinned outside a stock governor profile. Tooltip shows the active min–max range.
  - `UNKNOWN/ERROR`: warning icon if `cpupower` is missing, unsupported, or a read fails.
- **Interactive Context Menu:**
  - Quick-switch entries for each available governor (populated at runtime from `cpupower frequency-info --governors`, not hardcoded — hardware/driver support varies).
  - **Set Frequency Range...** — opens a small dialog for min/max frequency (`cpupower frequency-set -d -u`), pre-filled with current hardware limits from `frequency-info --hwlimits`.
  - **Refresh** — force an immediate re-poll.
  - **Quit** — exits Perf-Dock (does not revert governor changes on exit).
  - Currently-active governor is checked/highlighted; unavailable governors (not in the hardware's supported list) are hidden or disabled.

### 3.2. Real-Time State Monitor & Subprocess Controller
- Wraps `cpupower frequency-set` / `cpupower frequency-info` in safe subprocess calls (mirrors `NerdDockController`).
- Background polling loop (default interval configurable, e.g. 1–2s — CPU state changes less urgently than dictation state) reads current governor and frequency via `cpupower frequency-info -p` / `-f`.
- Updates tray icon/tooltip thread-safely via `GLib.idle_add`, matching nerd-dock's monitor-to-UI handoff pattern.
- All privileged mutations (`frequency-set`) go through a single, explicit escalation path (e.g. `pkexec`) — Perf-Dock itself never runs as root continuously.

### 3.3. Multi-Core Awareness
- By default, apply changes to all related CPUs (`-r`/`--related`), matching typical desktop expectations of "one setting for the whole machine."
- Per-core control is out of scope for v1 (flagged as a future enhancement, not a v1 requirement).

---

## 4. System States

| State | Governor | Description |
|---|---|---|
| `PERFORMANCE` | `performance` | CPU pinned to run at/near max frequency at all times. |
| `POWERSAVE` | `powersave` | CPU pinned to run at/near min frequency; battery/thermal priority. |
| `BALANCED` | `ondemand` / `schedutil` / `conservative` | Governor dynamically scales frequency with load. |
| `CUSTOM` | any | User has explicitly pinned a min/max range outside a single stock governor default. |
| `UNKNOWN/ERROR` | n/a | `cpupower` not installed, no permission, or unsupported driver on this hardware. |

---

## 5. Risks & Open Questions (flag to Morpheus before architecture)
- **Privilege escalation approach:** `pkexec` + a `.policy` file vs. a sudoers rule vs. a small privileged helper — needs an architectural decision before implementation.
- **Conflict with `power-profiles-daemon`:** many modern GNOME desktops already manage power profiles via `powerprofilesctl`/`power-profiles-daemon`, which can fight with direct `cpupower` governor changes. Needs investigation — may require detecting/pausing that daemon or documenting the conflict.
- **Hardware/driver variability:** available governors and frequency steps differ per driver (`acpi-cpufreq`, `intel_pstate`, `scmi`, etc.) — the UI must read capabilities at runtime, never assume a fixed governor list.

---

## 6. Development & Verification Automation
Reuses the nerd-dock quality bar (`Makefile.prj` pattern):
- **Style & Format:** `ruff check` / `ruff format`.
- **Complexity:** `radon cc`.
- **Dead Code:** `vulture`.
- **Security:** `bandit` (subprocess/privilege-escalation code paths get particular scrutiny here).
- **Duplication:** `pylint --disable=all --enable=duplicate-code`.
