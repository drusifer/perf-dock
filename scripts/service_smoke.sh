#!/usr/bin/env bash
set -euo pipefail

: "${PYTHON_BIN:?PYTHON_BIN must point to the project Python interpreter}"

PYTHONPATH=. "$PYTHON_BIN" -m perf_dock.main --gapplication-service &
service_pid=$!
cleanup() {
    if kill -0 "$service_pid" 2>/dev/null; then
        kill "$service_pid"
        wait "$service_pid" || true
    fi
}
trap cleanup EXIT

gdbus wait --session io.github.perf_dock
gdbus call --session \
    --dest io.github.perf_dock \
    --object-path /io/github/perf_dock \
    --method io.github.perf_dock.Control1.GetSnapshot
gdbus call --session \
    --dest io.github.perf_dock \
    --object-path /io/github/perf_dock \
    --method io.github.perf_dock.Control1.GetGovernors
gdbus call --session \
    --dest io.github.perf_dock \
    --object-path /io/github/perf_dock \
    --method io.github.perf_dock.Control1.Quit
wait "$service_pid"
trap - EXIT
