"""Integration test: validates PerfDockController's cpupower command syntax
against the REAL cpupower binary (no subprocess mocking).

This exists because a mocked-only test suite can assert a command list that
is internally consistent but wrong — as happened when `-r` was placed before
`frequency-set` (a global-option position) instead of after it (its actual
position, per `cpupower-frequency-set(1)`). `cpupower` rejects that ordering
with "Unknown option: -r" before privilege is even checked. This test runs
the real binary, unprivileged, and only asserts that argument *parsing*
succeeds (gets far enough to hit the root-privilege check) — it never
actually applies a change, so it's safe to run without pkexec/root.

The argv shape here (`[cpupower_path, "frequency-set", "-r", *args]`) must be
kept in sync with `PerfDockController._run_privileged`'s command list (minus
the leading `"pkexec"`, which we skip so this can run unprivileged).
"""

import shutil
import subprocess
import unittest

CPUPOWER_PATH = shutil.which("cpupower")


@unittest.skipUnless(CPUPOWER_PATH, "cpupower not installed on this machine")
class TestControllerCommandSyntax(unittest.TestCase):
    def _run_unprivileged(self, args: list[str]) -> subprocess.CompletedProcess:
        command = [CPUPOWER_PATH, "frequency-set", "-r", *args]
        return subprocess.run(  # nosec B603
            command, capture_output=True, text=True, check=False
        )

    def test_set_governor_args_are_accepted_by_real_cpupower(self) -> None:
        result = self._run_unprivileged(["-g", "performance"])
        self.assertNotIn("Unknown option", result.stderr + result.stdout)

    def test_set_range_args_are_accepted_by_real_cpupower(self) -> None:
        result = self._run_unprivileged(["-d", "1000000kHz", "-u", "2000000kHz"])
        self.assertNotIn("Unknown option", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
