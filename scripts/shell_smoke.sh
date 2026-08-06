#!/usr/bin/env bash
set -euo pipefail

readonly uuid="perf-dock@drusifer"
readonly log_file="${TMPDIR:-/tmp}/perf-dock-shell-smoke.log"

gnome-shell --devkit --wayland >"$log_file" 2>&1 &
shell_pid=$!
cleanup() {
    if kill -0 "$shell_pid" 2>/dev/null; then
        kill "$shell_pid"
        wait "$shell_pid" || true
    fi
}
trap cleanup EXIT

timeout 30 gdbus wait --session org.gnome.Shell
gnome-extensions enable "$uuid"
sleep 3
info="$(gnome-extensions info "$uuid")"
echo "$info"
if ! grep -Eq 'State: (ACTIVE|ENABLED)' <<<"$info"; then
    echo "Nested Shell did not enable $uuid. Log: $log_file" >&2
    exit 1
fi
if grep -E 'JS ERROR|Extension .* ERROR|perf-dock.*Error' "$log_file"; then
    echo "Perf-Dock produced a Shell error. Log: $log_file" >&2
    exit 1
fi

cleanup
trap - EXIT
echo "Nested GNOME Shell loaded and enabled $uuid without errors."
