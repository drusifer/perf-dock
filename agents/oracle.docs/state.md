# Oracle State

## Context

Perf-Dock now has two deliberately distinct interfaces: a full standalone
AppIndicator and a GNOME Shell 50 KISS extension showing all available governor
buttons directly.

## Recent Decisions
- Groomed docs for perf-dock v1 sprint: wrote README.md and docs/USER_GUIDE.md (both mirroring nerd-dock's structure/tone), updated memory.md's Project Context (was still template/Bob-Protocol placeholder) and Major Decisions table, added lessons.md entries for real defects found this session.

## Key Findings
- `agents/oracle.docs/memory.md` and `lessons.md` still had generic bob-protocol template content (Project Name: "Bob Protocol") before this sprint — first real project-specific grooming pass for perf-dock.
- Two "mocked tests validate a self-consistent bug" incidents this sprint (classify_state precision, cpupower -r flag position) — the pattern (not just the specific bugs) was promoted out of this project's local lessons.md into Trin's persona `SKILL.md` so future bob-protocol projects carry it by default.
- This project's bob-protocol scaffolding was missing `.mcp.json`/`.via/` in `.gitignore` (nerd-dock had them, perf-dock didn't) — traced to a gap in `agents/tools/setup_agent_links.py`, now fixed with an idempotent `ensure_gitignore_entries()`.

## Important Notes
- CHAT.md is short (well under 100 lines as of 2026-07-30), no archiving needed yet.
- This project's own `agents/*.docs/` state files were migrated from the 3-file (`context.md`/`current_task.md`/`next_steps.md`) convention to the new consolidated `state.md` on 2026-07-30, alongside the same change to the shared bob-protocol skill files.
- Shell extension sprint and documentation were committed and pushed to
  `origin/main` as `2f1c439` on 2026-08-05.

## Current Task

**Status:** Complete — Shell extension post-UAT grooming
**Assigned to:** Oracle
**Started:** 2026-08-05

### Task Description
Reconcile documentation with the live-tested Shell extension design and close
the Shell extension sprint board.

### Progress
- [x] Updated Shell architecture from proposed configurable popup to the final
  menu-free, all-governor panel design.
- [x] Updated US-6 through US-9 acceptance criteria and closed `task.md`.
- [x] Added Shell extension install/usage guidance and README navigation.
- [x] Preserved standalone AppIndicator menu/range documentation as a distinct
  interface.
- [x] Recorded the KISS UI and truthful-tooltip decisions in project memory.

### Blockers
None.

## Next Steps

### Immediate Next Action
None. Repository is ready for shutdown; resume from `origin/main` at `2f1c439`.

### Waiting On
Nothing.

---
*Last updated: 2026-08-05*
