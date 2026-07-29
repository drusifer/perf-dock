#!/usr/bin/env bash
# Automated smoke test: boots the real GTK tray app briefly against whatever
# display session and cpupower this machine actually has, then verifies it
# initialized cleanly and shut down without errors.
#
# This exists because mocked unit tests can validate a self-consistent bug
# (see agents/oracle.docs/lessons.md, 2026-07-29) — this target is the
# automated stand-in for the manual "run it for real" check Smith did by hand
# during the v1 sprint's end-to-end test.
set -uo pipefail

DURATION="${E2E_DURATION:-5}"
LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
    echo "e2e: no DISPLAY/WAYLAND_DISPLAY available — skipping (requires a real GTK session)."
    exit 0
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
timeout "$DURATION" "$PYTHON_BIN" -m perf_dock.main --verbose > "$LOG" 2>&1
status=$?

# GNU `timeout` reports 124 when it had to kill a still-running (i.e.
# not-crashed) process; that is the expected outcome here.
if [ "$status" -ne 124 ] && [ "$status" -ne 0 ]; then
    echo "e2e: perf-dock exited early with status $status"
    cat "$LOG"
    exit 1
fi

if ! grep -q "Perf-Dock is successfully loaded" "$LOG"; then
    echo "e2e: startup marker not found in log"
    cat "$LOG"
    exit 1
fi

if grep -qi "Traceback\|CRITICAL" "$LOG"; then
    echo "e2e: unexpected error in log"
    cat "$LOG"
    exit 1
fi

if ! grep -q "Monitor thread stopped" "$LOG"; then
    echo "e2e: clean shutdown marker not found in log"
    cat "$LOG"
    exit 1
fi

echo "e2e: perf-dock booted cleanly, ran ${DURATION}s, shut down cleanly, no errors."
