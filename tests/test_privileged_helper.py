"""Security-boundary tests for the installed Perf-Dock privilege helper."""

import runpy
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


class TestPrivilegedHelper(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        helper_path = Path(__file__).parents[1] / "scripts" / "perf-dock-helper"
        cls.helper: dict[str, Any] = runpy.run_path(str(helper_path))
        cls.helper["build_command"].__globals__["cpupower_path"] = lambda: (
            "/usr/bin/cpupower"
        )

    def test_governor_builds_fixed_cpupower_command(self) -> None:
        self.assertEqual(
            self.helper["build_command"](["governor", "performance"]),
            [
                "/usr/bin/cpupower",
                "frequency-set",
                "-r",
                "-g",
                "performance",
            ],
        )

    def test_range_builds_fixed_cpupower_command(self) -> None:
        self.assertEqual(
            self.helper["build_command"](["range", "1000000", "2000000"]),
            [
                "/usr/bin/cpupower",
                "frequency-set",
                "-r",
                "-d",
                "1000000kHz",
                "-u",
                "2000000kHz",
            ],
        )

    def test_rejects_injected_governor(self) -> None:
        with self.assertRaises(SystemExit):
            self.helper["build_command"](["governor", "performance;sh"])

    def test_rejects_non_numeric_frequency(self) -> None:
        with self.assertRaises(SystemExit):
            self.helper["build_command"](["range", "1GHz", "-"])

    def test_rejects_reversed_range(self) -> None:
        with self.assertRaises(SystemExit):
            self.helper["build_command"](["range", "2000000", "1000000"])

    def test_rejects_unknown_operation(self) -> None:
        with self.assertRaises(SystemExit):
            self.helper["build_command"](["shell"])

    def test_polkit_policy_is_scoped_and_retained(self) -> None:
        policy_path = (
            Path(__file__).parents[1] / "packaging" / "io.github.perf-dock.policy"
        )
        action = ET.parse(policy_path).getroot().find("action")  # noqa: S314
        self.assertIsNotNone(action)
        self.assertEqual(action.get("id"), "io.github.perf-dock.set-frequency")
        self.assertEqual(action.findtext("defaults/allow_active"), "auth_admin_keep")
        annotation = action.find("annotate")
        self.assertEqual(annotation.get("key"), "org.freedesktop.policykit.exec.path")
        self.assertEqual(annotation.text, "/usr/libexec/perf-dock-helper")


if __name__ == "__main__":
    unittest.main()
