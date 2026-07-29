# Sprint Backlog — Perf-Dock Implementation

Decomposed per ARCH.md into **4 short, focused phases** (mirrors nerd-dock's phase structure), each independent with small task counts to avoid context overflow.

---

## Sprint Goals
- **High-level Objective:** Deliver a working GNOME top-bar tray applet wrapping `cpupower frequency-set`/`frequency-info`, with runtime-discovered governor menu, frequency-range dialog, real-time sync, safe pkexec-based privilege escalation, and a full static-analysis/test pipeline — per docs/PRD.md, docs/USER_STORIES.md (US-1..5), and docs/ARCH.md.

---

## 📋 Phase 1: Environment Setup & Dev Tools
- [ ] **Task 1.1:** `pyproject.toml` (PEP 518) + `Makefile.prj` with lint/test/format/clean targets (mirrors nerd-dock).
- [ ] **Task 1.2:** Package skeleton `perf_dock/{__init__.py, main.py}` + `resources/icons/*.svg` (performance/powersave/balanced/custom/error).
- [ ] **Task 1.3:** Test harness scaffolding under `tests/` with mock helpers for `subprocess`/`shutil.which`.

## 📋 Phase 2: Core Logic (Read Layer + State + Controller)
- [ ] **Task 2.1:** Implement `cpufreq.py` (governors/hwlimits/policy parsing, `CpuFreqUnavailableError`) + `test_cpufreq.py`.
- [ ] **Task 2.2:** Implement `state.py` pure `classify_state()` + `test_state.py`.
- [ ] **Task 2.3:** Implement `controller.py` (`PerfDockController`: set_governor/set_range/restore_default_range, pkexec escalation, `is_busy`) + `ppd_check.py` + `test_controller.py`.

## 📋 Phase 3: Monitor & Tray UI
- [ ] **Task 3.1:** Implement `monitor.py` (`PerfDockMonitor` poll loop, `GLib.idle_add` dispatch) + `test_monitor.py`.
- [ ] **Task 3.2:** Implement `ui_indicator.py` (`PerfDockIndicator`: dynamic icons, runtime governor menu, frequency dialog, restore-default item, error state, ppd advisory note).
- [ ] **Task 3.3:** Wire `main.py` entry point (CLI args: `--poll-interval`, `--verbose`) tying controller + monitor + indicator together.

## 📋 Phase 4: Static Analysis & Verification
- [ ] **Task 4.1:** `make lint` clean pass: `ruff`, `radon`, `vulture`, `bandit`, `pylint --enable=duplicate-code`.
- [ ] **Task 4.2:** `make test` clean pass, coverage on `cpufreq.py`/`state.py`/`controller.py`/`monitor.py`.
- [ ] **Task 4.3:** Smith end-to-end usability test against US-1..5 acceptance criteria; retro; Cypher launch.

---
*Maintained by Mouse. Last updated: 2026-07-29.*
