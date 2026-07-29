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
| 2026-07-29 | Privilege escalation via plain `pkexec <abs cpupower path> -r frequency-set ...`, default polkit policy | Satisfies "no standing privilege" requirement with zero packaging overhead (no custom `.policy` XML to ship) | Every mutating action prompts for a password; custom scoped policy action deferred to v2 |
| 2026-07-29 | power-profiles-daemon: detect-only via `systemctl is-active`, surfaced as advisory text | v1 does not fight or pause the daemon | Known limitation documented in tray tooltip; "offer to pause ppd" is a v2 backlog item |
| 2026-07-29 | `cpufreq.py` parses targeted `cpupower frequency-info` flags (`-g`, `-l`, `-p`) instead of the full-text dump wherever a flag exists | `-l --hwlimits` gives clean machine-readable kHz output; far less fragile than regexing prose | `get_frequency_steps()` still has to parse the full-text dump since no dedicated flag exists for step list |

## Repository Structure Memory
- `agents/`: Contains persona-specific documentation and state.
- `docs/`: Global documentation (PRD, Architecture, etc.).
- `task.md`: Single source of truth for the current sprint (maintained by Mouse).
