# Morpheus State

## Context

## Recent Decisions
- Privilege escalation: plain `pkexec <absolute cpupower path> frequency-set -r ...`, default polkit policy (no custom .policy file for v1). Rationale: satisfies US-4 with zero packaging overhead; custom scoped action deferred to v2.
- power-profiles-daemon conflict: detect-only via `systemctl is-active power-profiles-daemon`, surfaced as advisory text, not fought/disabled in v1.
- Parsing strategy: use targeted `cpupower frequency-info` flags (`-g`, `-l`, `-p`) instead of parsing the full-text dump — `-l --hwlimits` gives clean numeric kHz output, most robust of the three.
- State classification (`state.py`) is a pure function with no I/O — `classify_state(governor, policy_min, policy_max, hw_min, hw_max)` — trivially unit-testable. Uses a tolerance (not exact equality) since `-p` and `-l` differ in rounding precision (found post-launch via real-hardware testing).
- Shell Extension: GNOME Shell 50 GJS frontend uses adjacent supported
  `PanelMenu.Button` actors and async session D-Bus; Python becomes an
  activatable unprivileged service owning controller/monitor/dialogs. Existing
  AppIndicator mode remains the fallback. No private Shell actor insertion and
  no privileged commands in GJS.

## Key Findings
- Confirmed on this dev machine: `power-profiles-daemon` is active, `pkexec` and `cpupower` both present at `/usr/bin/`.
- `cpupower frequency-info` (no flags) prints "analyzing CPU N" for an arbitrary representative core, not always CPU 0 — parsing must not assume CPU 0.
- Real bug found post-launch: `-r`/`--related` is a `frequency-set` subcommand option, not a global `cpupower` flag — must come after `frequency-set`, not before. Fixed by Neo; caught by a real user, not by review.

## Important Notes
- Package layout: perf_dock/{cpufreq,state,controller,monitor,ppd_check,ui_indicator}.py — mirrors nerd-dock's module split but adds state.py (pure logic) and ppd_check.py (new risk-mitigation module) not present in nerd-dock.

## Current Task

**Status:** Shell Extension plan approved; Phase 1 ready
**Assigned to:** Morpheus
**Started:** 2026-07-29

### Task Description
Architect perf-dock, review sprint plan, and code-review the finished implementation.

### Progress
- [x] Wrote docs/ARCH.md.
- [x] Smith Gate 2 approved.
- [x] Reviewed and approved Mouse's sprint_log.md phase breakdown (Step 3a).
- [x] Code review of Phases 1-3 (all modules): PASS.
- [x] Approved one accepted deviation: is_busy() enforced via early-return guards, not set_sensitive(False).
- [x] Designed GNOME 50 extension, Control1 D-Bus contract, GSettings
  persistence, panel/menu behavior, user-local lifecycle, and nested-Shell test
  strategy in `docs/SHELL_EXTENSION_ARCH.md`.
- [x] Reviewed root `task.md`: PASS. Phase boundaries follow dependency order,
  each contains 1-3 implementation concerns plus an explicit QA/review gate,
  and Tank-owned lifecycle work is correctly last.

### Blockers
None.

## Next Steps

### Immediate Next Action
Neo implements Phase 1 contract tests and D-Bus backend service only.

### Waiting On
Phase 1 Neo handoff.

---
*Last updated: 2026-07-30 18:26 EDT*
