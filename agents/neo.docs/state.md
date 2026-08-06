# Neo State

## Context

## Recent Decisions
- Implemented Phases 1-3 in one pass rather than strictly sequential (scaffolding, cpufreq/state/controller/monitor, ui_indicator/main) since they're tightly coupled and small enough to reason about together.
- `pyproject.toml` ruff ignore list needed 2 additions beyond nerd-dock's: `S607` (partial exec path — pkexec/systemctl/cpupower resolved via $PATH by design) and `PT019` (unittest.mock.patch injects args we intentionally don't use, not real pytest fixtures).
- Bandit needs inline `# nosec B404`/`B603`/`B607` comments (not ruff ignores) on every subprocess import/call — same pattern nerd-dock used.
- `cpupower frequency-info` has no dedicated flag for the frequency-steps list; `get_frequency_steps()` falls back to parsing the full-text dump (only place we do this) since no flag exists.
- Post-launch: `-r`/`--related` must come AFTER `frequency-set`, not before — it's a subcommand option, not a global flag. Fixed in `controller.py`'s `_run_privileged`; added `tests/test_controller_integration.py` running the real unprivileged binary so this class of bug can't recur silently.

## Key Findings
- Vulture caught 2 genuinely dead/half-wired things during lint: `get_state()` was truly unused (removed); `is_busy()`/`cpufreq.is_available()` were defined but never called — wired both in for real.
- The Makefile.prj `test`/`lint`/etc. targets are NOT usable via `make <target>` unless stubbed in the root Makefile's `else` block too. Same gap hit twice: once for setup/run/lint/etc., once for `judge-trace`.
- Two mocked-test traps found this session, same root cause (mocks validate the test author's assumptions, not reality): `classify_state()`'s exact-equality bug (cpupower `-p`/`-l` precision mismatch), and the `-r` flag-position bug (mocked assertions matched the wrong command verbatim). See `agents/oracle.docs/lessons.md`.

## Important Notes
- `make lint` clean (ruff/radon/vulture/bandit/pylint, pylint 10.00/10). `make test`: 55/55 passing (includes `tests/test_trace_annotate.py`, added during the judge loop).
- venv is at `/home/drusifer/Projects/perf-dock/venv` (created via `make setup`), has all dev deps installed.

## Current Task

**Status:** Scoped Polkit authorization implemented and verified; local install pending
**Assigned to:** Neo
**Started:** 2026-07-29

### Task Description
Implement perf-dock per docs/PRD.md, docs/USER_STORIES.md, docs/ARCH.md, agents/mouse.docs/sprint_log.md. Post-launch: fix user-reported bug, fix judge-loop-cataloged tooling bugs.

### Progress
- [x] Phases 1-3 implemented, Trin UAT (4 gaps fixed), Morpheus review PASS.
- [x] Smith e2e found + fixed `classify_state()` precision bug; added `make e2e`.
- [x] User-reported `cpupower -r` flag-position bug fixed post-launch; added integration test.
- [x] Judge loop BUG-001 fixed: `MAKE_BYPASS_RE` quote-blindness in `agents/tools/trace_annotate.py`; also fixed a related `VENV_RE` dotless-venv gap. Added `tests/test_trace_annotate.py`.
- [x] Added a root-owned, argument-validating Perf-Dock helper and dedicated
  `auth_admin_keep` Polkit action so repeated frequency changes reuse a brief
  authorization instead of prompting every time.
- [x] Added `make install-polkit`, documentation, and security-boundary tests;
  63 tests and full lint pass.

### Blockers
The execution channel cannot enter the user's sudo password. The user must run
`make install-polkit` once in an interactive terminal; no system files have yet
been installed.

## Next Steps

### Immediate Next Action
User runs `make install-polkit`, then launches/restarts Perf-Dock and confirms
that one successful authentication covers several governor/range changes.

### Waiting On
Interactive system installation by the user.

---
*Last updated: 2026-07-30 15:33 EDT*
