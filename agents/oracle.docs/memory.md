# Project Memory

This file serves as a consolidated index of project-wide decisions, historical context, and key milestones. It is maintained by the Oracle and reviewed by all agents to ensure consistency.

## Project Context
- **Project Name:** Perf-Dock
- **Start Date:** 2026-07-29
- **Key Objectives:** GNOME tray applet wrapping `cpupower frequency-set`/`frequency-info`, modeled on the sibling project `../nerd-dock`. See `docs/PRD.md`, `docs/USER_STORIES.md`, `docs/ARCH.md`.

## Major Decisions
| Date | Decision | Rationale | Consequences |
|------|----------|-----------|--------------|
| 2026-05-06 | Artifact-Based Verification | Chat latency and missed messages | Agents read docs directly; higher autonomy |
| 2026-07-29 / 2026-08-05 | Privilege escalation uses a root-owned, narrowly scoped helper and dedicated Polkit action with short-lived retained authorization | Avoids repeated prompts while authorizing only validated governor/range mutations, not arbitrary commands | `make install-polkit` is a separate privileged installation; neither extension nor service runs as root |
| 2026-07-29 | power-profiles-daemon: detect-only via `systemctl is-active`, surfaced as advisory text | v1 does not fight or pause the daemon | Known limitation documented in tray tooltip; "offer to pause ppd" is a v2 backlog item |
| 2026-07-29 | `cpufreq.py` parses targeted `cpupower frequency-info` flags (`-g`, `-l`, `-p`) instead of the full-text dump wherever a flag exists | `-l --hwlimits` gives clean machine-readable kHz output; far less fragile than regexing prose | `get_frequency_steps()` still has to parse the full-text dump since no dedicated flag exists for step list |
| 2026-08-05 | GNOME Shell extension uses a KISS six-button, menu-free surface | Live user testing found the combined popup, visibility toggles, lifecycle actions, and range controls ambiguous or unnecessary | Every available governor is always visible and directly selectable; the standalone AppIndicator remains the richer interface |
| 2026-08-05 | Governor tooltips describe behavior rather than per-mode frequency ranges | Linux governors share policy limits and do not own distinct frequency ranges | Active state is explicit without presenting repeated or invented range data |

## Repository Structure Memory
- `agents/`: Contains persona-specific documentation and state.
- `docs/`: Global documentation (PRD, Architecture, etc.).
- `task.md`: Single source of truth for the current sprint (maintained by Mouse).
