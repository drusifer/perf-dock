# Trin Context

## Recent Decisions
- UAT for perf-dock is done by reading the actual acceptance-criteria strings in docs/USER_STORIES.md and diffing them against the real label/behavior in code, not just running the test suite — the test suite passing does not prove the acceptance criteria are met if the tests were written to match buggy code.

## Key Findings
- First UAT pass on Phases 1-3 found 4 real gaps despite 37/37 tests passing at the time: label format didn't match spec exactly for PERFORMANCE/POWERSAVE, CUSTOM state didn't show the numeric range, no input validation on the frequency dialog (min>max), no user-facing notification on cancelled/failed privileged actions. All fixed and reverified in one retry (no Oracle escalation needed).

## Important Notes
- Current state (2026-07-29): 40/40 tests passing, `make lint` clean (ruff/radon/vulture/bandit/pylint), all US-1/US-2/US-4 acceptance criteria verified directly against code.

---
*Last updated: 2026-07-29*
