# Neo Context

## Recent Decisions
- Implemented Phases 1-3 in one pass rather than strictly sequential (scaffolding, cpufreq/state/controller/monitor, ui_indicator/main) since they're tightly coupled and small enough to reason about together.
- `pyproject.toml` ruff ignore list needed 2 additions beyond nerd-dock's: `S607` (partial exec path — pkexec/systemctl/cpupower resolved via $PATH by design) and `PT019` (unittest.mock.patch injects args we intentionally don't use, not real pytest fixtures).
- Bandit needs inline `# nosec B404`/`B603`/`B607` comments (not ruff ignores) on every subprocess import/call — same pattern nerd-dock used.
- `cpupower frequency-info` has no dedicated flag for the frequency-steps list; `get_frequency_steps()` falls back to parsing the full-text dump (only place we do this) since no flag exists.

## Key Findings
- Vulture caught 2 genuinely dead/half-wired things during lint: `get_state()` was truly unused (removed, redundant with `StateSnapshot.state`); `is_busy()` and `cpufreq.is_available()` were defined per ARCH.md but never actually called anywhere — wired `is_busy()` into the three UI action handlers (governor toggle, range dialog, restore) to guard against a real reentrancy edge case (Gtk.Dialog.run() runs a nested main loop, so the tray's own menu can still fire while a dialog is open), and wired `is_available()` into `main.py` for an early startup warning.
- The Makefile.prj `test`/`lint`/etc. targets are NOT usable via `make <target>` unless stubbed in the root Makefile's `else` block too (see `.claude/skills/make` "Adding a new target"). Had to add stubs for setup/run/lint/format/clean/install/install-system-deps to `/home/drusifer/Projects/perf-dock/Makefile`.

## Important Notes
- `make lint` clean (ruff/radon/vulture/bandit/pylint all pass, pylint 10.00/10). `make test` (via root Makefile's `python -m unittest discover`): 37/37 passing.
- venv is at `/home/drusifer/Projects/perf-dock/venv` (created via `make setup`), has all dev deps installed.

---
*Last updated: 2026-07-29*
