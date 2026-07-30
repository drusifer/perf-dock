# Bob State

## Context

## Recent Decisions
- Added a proactive-load nudge to `agents/skills/make/SKILL.md` after the judge loop found all confirmed `AP-MAKE-BYPASS`/`AP-MAKE-PIPE` violations happened before the `make` skill was loaded that session, none after.
- Consolidated the three-file persona state convention (`context.md`/`current_task.md`/`next_steps.md`) into a single `state.md` per persona across all `SKILL.md` files, `agents/skills/bob-protocol/SKILL.md`, `agents/templates/`, and the root `Makefile`'s install/update/clean_bob targets — cuts state-management tool calls per persona switch by two-thirds with no loss of resilience (still written every switch, just one file instead of three).
- Added a "Section-Scoped Reads" note to `agents/skills/via/SKILL.md`: `via -mg '*Section*' -tH` locates a line number, pair with scoped `Read(offset=..., limit=...)` for large growing docs (lessons.md, memory.md, ARCH.md) — verified `-oR -A N` is a blind line-count window, not section-aware, so it's not reliable alone for exact section bounds.

## Key Findings
- Bob's own `SKILL.md` was missing a full State Management Protocol ENTRY/EXIT section that every other persona has — only had a Working Memory table and an "Agent Template" example. Not fixed this session (out of scope for the state-file consolidation task), flagged here for a future `*reprompt`.

## Important Notes
- This is the first time Bob's state.md has been written with real content — previously always template/untouched.

## Current Task

**Status:** Idle — last active for the judge-loop prompt update (2026-07-29/30)
**Assigned to:** N/A
**Started:** N/A

### Task Description
No active task.

### Progress
- [x] Judge-loop prompt updates (make skill proactive-load note, judge skill live-session caveat) — complete.
- [x] State-file consolidation (3→1 per persona) across all SKILL.md files — complete.

### Blockers
None

## Next Steps

### Immediate Next Action
None planned.

### Waiting On
None

### Planned Work
- [ ] Consider adding a full State Management Protocol ENTRY/EXIT section to Bob's own SKILL.md (currently the only persona without one).

---
*Last updated: 2026-07-30*
