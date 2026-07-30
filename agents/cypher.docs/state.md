# Cypher State

## Context

## Recent Decisions
- perf-dock modeled directly on `../nerd-dock` (tray applet pattern, Makefile.prj lint suite, docs/ layout: PRD.md, USER_STORIES.md, ARCH.md, USER_GUIDE.md).
- Governor list is read at runtime from `cpupower frequency-info --governors`, never hardcoded — hardware/driver support varies (confirmed via `cpupower frequency-info` on this machine: driver `scmi`, governors conservative/ondemand/userspace/powersave/performance/schedutil).
- v1 scope is machine-wide control (`-r`/`--related`), not per-core. Per-core deferred to a future story.

## Key Findings
- `cpupower frequency-set` requires elevated privileges; `frequency-info` does not. This split drives US-4 (privilege escalation) and is flagged as an architectural risk for Morpheus.
- Possible conflict with GNOME `power-profiles-daemon` — resolved in ARCH.md (detect-only via systemctl, not fought/disabled in v1).

## Important Notes
- PRD.md and USER_STORIES.md written to `docs/` (2026-07-29).

## Current Task

**Status:** Sprint complete — v1 launched
**Assigned to:** Cypher
**Started:** 2026-07-29

### Task Description
Full sprint for perf-dock v1: PRD, user stories, gates, and launch.

### Progress
- [x] Wrote `docs/PRD.md` and `docs/USER_STORIES.md` (US-1 through US-5).
- [x] Gate 1 (Smith): approved with 3 amendments.
- [x] Morpheus architecture, Gate 2 (Smith): approved.
- [x] Mouse phase breakdown, Morpheus plan review: approved.
- [x] Phases 1-3 implemented, Trin UAT (4 gaps found+fixed), Morpheus code review: PASS.
- [x] Smith e2e test found+fixed a real classify_state() precision bug; added `make e2e` automated gate.
- [x] All-persona retro complete.
- [x] Launched (see CHAT.md `*pm launch`).
- [x] Post-launch: user found and Neo fixed a real `cpupower -r` flag-position bug in live use.

### Backlog for v2 (from retro)
- Custom polkit `.policy` file for nicer pkexec prompt copy.
- Lock-glyph cue on privileged menu items (Smith, Gate 2 note).
- Offer to pause `power-profiles-daemon` while Perf-Dock runs.
- Per-core frequency control.
- "Real data sample" fixture convention for cpupower-adjacent parsing tests (Trin retro).
- Human interactive smoke-test of tray menu/dialog/pkexec click-through (Smith flagged this as untested in-session).

### Blockers
None.

## Next Steps

### Immediate Next Action
None — v1 shipped and a live bug already fixed. Next session: prioritize the v2 backlog above with the user, starting with the human interactive smoke-test (highest-risk untested path) and the polkit `.policy` UX polish.

### Waiting On
User direction on v2 priorities.

---
*Last updated: 2026-07-30*
