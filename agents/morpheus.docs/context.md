# Morpheus Context

## Recent Decisions
- Privilege escalation: plain `pkexec <absolute cpupower path> -r frequency-set ...`, default polkit policy (no custom .policy file for v1). Rationale: satisfies US-4 with zero packaging overhead; custom scoped action deferred to v2.
- power-profiles-daemon conflict: detect-only via `systemctl is-active power-profiles-daemon`, surfaced as advisory text, not fought/disabled in v1.
- Parsing strategy: use targeted `cpupower frequency-info` flags (`-g`, `-l`, `-p`) instead of parsing the full-text dump — `-l --hwlimits` gives clean numeric kHz output, most robust of the three.
- State classification (`state.py`) is a pure function with no I/O — `classify_state(governor, policy_min, policy_max, hw_min, hw_max)` — trivially unit-testable.

## Key Findings
- Confirmed on this dev machine: `power-profiles-daemon` is active, `pkexec` and `cpupower` both present at `/usr/bin/`. `cpupower frequency-info -p/-l/-g` outputs verified directly (see ARCH.md §2.1 for exact formats).
- `cpupower frequency-info` (no flags) prints "analyzing CPU N" for an arbitrary representative core, not always CPU 0 — parsing must not assume CPU 0.

## Important Notes
- ARCH.md written 2026-07-29, status Draft — Pending Smith Gate 2.
- Package layout: perf_dock/{cpufreq,state,controller,monitor,ppd_check,ui_indicator}.py — mirrors nerd-dock's module split but adds state.py (pure logic) and ppd_check.py (new risk-mitigation module) not present in nerd-dock.

---
*Last updated: 2026-07-29*
