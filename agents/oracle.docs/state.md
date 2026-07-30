# Oracle State

## Context

## Recent Decisions
- Groomed docs for perf-dock v1 sprint: wrote README.md and docs/USER_GUIDE.md (both mirroring nerd-dock's structure/tone), updated memory.md's Project Context (was still template/Bob-Protocol placeholder) and Major Decisions table, added lessons.md entries for real defects found this session.

## Key Findings
- `agents/oracle.docs/memory.md` and `lessons.md` still had generic bob-protocol template content (Project Name: "Bob Protocol") before this sprint — first real project-specific grooming pass for perf-dock.
- Two "mocked tests validate a self-consistent bug" incidents this sprint (classify_state precision, cpupower -r flag position) — the pattern (not just the specific bugs) was promoted out of this project's local lessons.md into Trin's persona `SKILL.md` so future bob-protocol projects carry it by default.
- This project's bob-protocol scaffolding was missing `.mcp.json`/`.via/` in `.gitignore` (nerd-dock had them, perf-dock didn't) — traced to a gap in `agents/tools/setup_agent_links.py`, now fixed with an idempotent `ensure_gitignore_entries()`.

## Important Notes
- CHAT.md is short (well under 100 lines as of 2026-07-30), no archiving needed yet.
- This project's own `agents/*.docs/` state files were migrated from the 3-file (`context.md`/`current_task.md`/`next_steps.md`) convention to the new consolidated `state.md` on 2026-07-30, alongside the same change to the shared bob-protocol skill files.

## Current Task

**Status:** Groom complete for v1; skill/process improvements complete
**Assigned to:** Oracle
**Started:** 2026-07-29

### Task Description
Sprint-close grooming for perf-dock v1 (docs, memory, lessons), plus cross-project bob-protocol improvements after the user's review.

### Progress
- [x] Wrote README.md and docs/USER_GUIDE.md.
- [x] Updated memory.md and lessons.md (4 entries: Makefile.prj stub requirement, ruff/bandit config additions, classify_state precision bug, cpupower -r flag-position bug).
- [x] Smith end-to-end usability test, all-persona retro, Cypher launch — complete.
- [x] Post-launch skill improvements (user-approved): gitignore scaffolding fix, judge live-session caveat, Trin lesson promotion, state-file consolidation.

### Blockers
None.

## Next Steps

### Immediate Next Action
None — all agreed skill improvements are implemented. Available for the next `*ora groom` pass once v2 backlog work starts.

### Waiting On
Nothing.

---
*Last updated: 2026-07-30*
