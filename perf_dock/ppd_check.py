"""Best-effort detection of GNOME's power-profiles-daemon.

Advisory only (per ARCH.md Risk #2 resolution): perf-dock does not stop,
disable, or otherwise fight power-profiles-daemon in v1. This module only
answers "is it active?" so the UI can surface a non-blocking note. Any
failure to check (daemon absent, systemctl missing, permission denied) is
treated as "not active" — this check must never raise or block the tray.
"""

import subprocess  # nosec B404


def is_ppd_active() -> bool:
    """Returns True if power-profiles-daemon is currently active, else False."""
    try:
        result = subprocess.run(  # nosec B603 B607
            ["systemctl", "is-active", "power-profiles-daemon"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return result.stdout.strip() == "active"
