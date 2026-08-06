# Smith State

## Context

## Recent Decisions
- perf-dock v1 stories approved with amendments (2026-07-29): added "Restore Default Range" escape hatch (Nielsen #3) and missing-`cpupower` onboarding error state (Nielsen #9) to US-1; allowed independent min/max in US-2 (Nielsen #7 flexibility).
- Rich profile selector consult (2026-07-30): recommend visually distinct
  profile rows/cards with persistent names and ranges; hover text is useful as
  supplemental detail but must not be the only way to discover either value.
- User clarified the target is an always-visible GNOME panel control group:
  `[Powersave] [Schedutil] [Performance] [Menu]`, not a dropdown. Recommend a
  GNOME Shell extension frontend; one AppIndicator cannot expose four true
  independent primary-click targets in a single panel segment.

## Key Findings
- Real-hardware e2e testing (not just mocked UAT) caught a genuine defect the mocked test suite missed: `classify_state()`'s precision-mismatch bug. Confirms Smith's "actually run the software" mandate has real teeth, not just ceremony.
- Residual risk flagged at launch: no interactive click-through of tray menu/dialog/pkexec was possible in-session (no GUI-automation tool). That risk materialized — the user hit a real `cpupower -r` flag-position bug on first live use, which Neo then fixed.
- Current `Gtk.RadioMenuItem` rows already expose mutually exclusive governors
  and mark the current selection. Ayatana AppIndicator requires a `Gtk.Menu`;
  a dependable cross-desktop horizontal card/button layout should therefore be
  a separate compact GTK control window, while an enriched dropdown should use
  normal menu rows.

## Important Notes
- Both sprint gates (US-1 review, ARCH.md review) and the end-to-end test are complete and passed.

## Current Task

**Status:** Shell Extension Gates 1 and 2 approved
**Assigned to:** Smith
**Started:** 2026-07-29

### Task Description
Sprint gates for perf-dock v1, plus judge-loop trace evaluation.

### Progress
- [x] Gate 1: reviewed docs/USER_STORIES.md, added 3 amendments, approved.
- [x] Gate 2: reviewed docs/ARCH.md, approved with 1 non-blocking backlog note.
- [x] End-to-end usability test: found and filed the classify_state() real-hardware bug (fixed), then approved after re-verification.
- [x] Residual risk (interactive click-through untested) materialized post-launch and was fixed.
- [x] Judge loop: scored session TES 76/100, filed BUG-001 (MAKE_BYPASS_RE quote-blindness) for Neo.
- [x] Gate 1 Shell Extension: US-6..US-9 approved. Criteria cover
  recognition, non-color selection state, pending/error feedback, keyboard
  discoverability, persistence, recovery, and the existing menu fallback.
- [x] Gate 2 Shell Extension: approved GNOME 50 panel + async D-Bus service
  split. It preserves menu parity/fallback, prevents Shell blocking, supports
  reconnect/error recovery, and gives hover and keyboard focus equivalent help.

### Blockers
None at Gate 1.

## Next Steps

### Immediate Next Action
Mouse decomposes the architecture into short backend-contract, extension-UI,
and integration/install phases.

### Waiting On
Mouse sprint plan.

---
*Last updated: 2026-07-30 15:49 EDT*
