# Cypher Context

## Recent Decisions
- perf-dock modeled directly on `../nerd-dock` (tray applet pattern, Makefile.prj lint suite, docs/ layout: PRD.md, USER_STORIES.md, ARCH.md, USER_GUIDE.md).
- Governor list is read at runtime from `cpupower frequency-info --governors`, never hardcoded — hardware/driver support varies (confirmed via `cpupower frequency-info` on this machine: driver `scmi`, governors conservative/ondemand/userspace/powersave/performance/schedutil).
- v1 scope is machine-wide control (`-r`/`--related`), not per-core. Per-core deferred to a future story.

## Key Findings
- `cpupower frequency-set` requires elevated privileges; `frequency-info` does not. This split drives US-4 (privilege escalation) and is flagged as an architectural risk for Morpheus.
- Possible conflict with GNOME `power-profiles-daemon` — not resolved, flagged as an open question in PRD.md section 5, needs Morpheus/Neo investigation before/during implementation.

## Important Notes
- PRD.md and USER_STORIES.md written to `docs/` (2026-07-29), status: Draft — Pending Smith Gate 1 review.
- Per protocol, next step is handoff to Smith (`*user review`) before this goes to Morpheus for architecture.

---
*Last updated: 2026-07-29*
