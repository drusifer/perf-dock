# Sprint Board — Shell Extension

**Sprint:** Perf-Dock GNOME Shell Extension
**Status:** Implemented; live UX iteration complete
**Goal:** Deliver one-click controls for every available governor in the GNOME
50 panel, backed by the existing safe controller.

## Phase 1 — Versioned Backend Service

- [x] **1.1 — Contract tests first (Neo):** Define and test the
  `io.github.perf_dock.Control1` introspection XML, snapshot serialization,
  governor validation, failure messages, and signal behavior.
- [x] **1.2 — D-Bus service (Neo):** Implement `perf_dock/service.py`, compose
  the existing controller/monitor, and add `--gapplication-service` without
  changing default AppIndicator mode.
- [x] **1.3 — Phase gate (Trin → Morpheus):** Verify Python tests, real read-only
  cpupower data, D-Bus activation/reconnect behavior, then architecture review.

## Phase 2 — Extension Model and D-Bus Contract

- [x] **2.1 — Extension scaffold (Neo):** Add GNOME 50 metadata, schema, symbolic
  icons, D-Bus proxy, and a pure projection model under `shell-extension/`.
- [x] **2.2 — Model tests (Neo):** Test D-Bus Variant normalization,
  alphabetical ordering, icon mapping, active/pending/error projection, and
  truthful tooltip formatting.
- [x] **2.3 — Phase gate (Trin → Morpheus):** Run GJS/schema/metadata checks and
  review extension lifecycle, async cleanup, and public-Shell-API use.

## Phase 3 — KISS Panel Controls

- [x] **3.1 — Panel group (Neo):** Render all available governor buttons in one
  menu-free group; implement one-click switching, selected/focus/
  pending/error styles, tooltips, and D-Bus reconnect.
- [x] **3.2 — UX simplification (Neo + user UAT):** Remove popup menu,
  frequency controls, lifecycle controls, and visibility configuration; show all
  six target-machine governors with distinct icons.
- [x] **3.3 — Phase gate (Trin → Morpheus):** Verify all US-6..US-8 interactions,
  keyboard/accessibility state, race prevention, cleanup, and AppIndicator
  regression behavior; complete architecture review.

## Phase 4 — Installation, Real GNOME Verification, and Release

- [x] **4.1 — Repeatable lifecycle automation (Tank):** Add Make targets for
  extension/service install, enable, disable, and uninstall with GNOME 50
  validation; keep Polkit installation independent and recoverable.
- [x] **4.2 — Nested and live-session verification (Trin + Smith):** Automate a
  GNOME 50 devkit smoke test where possible, then human-test real panel clicks,
  all-button rendering, hover/focus help, reconnect, and disable/re-enable.
- [x] **4.3 — Docs and release gates (Oracle → all):** Update user/install/
  architecture docs, run full Python/GJS/security regressions, retrospective,
  and Cypher launch.

## Definition of Done

- US-6 through US-9 pass.
- Existing US-1 through US-5 behavior remains available and regression-clean.
- No privileged command is constructed or executed by GJS.
- GNOME Shell remains responsive during authentication and backend failure.
- `make test`, `make lint`, contract tests, and GNOME 50 smoke checks pass.
- Interactive behavior is demonstrated in a real GNOME 50 session.

## Blockers

None.
