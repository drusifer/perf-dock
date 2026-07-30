"""Unit tests for agents/tools/trace_annotate.py's Bash command classifier.

Regression coverage for BUG-001 (judge loop, 2026-07-29): MAKE_BYPASS_RE
false-flagged `make chat MSG="..."` calls whose quoted message text merely
mentioned a tool name (e.g. "pylint 10/10") rather than actually invoking it.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent.parent / "agents" / "tools"
_MODULE_PATH = _TOOLS_DIR / "trace_annotate.py"
_spec = importlib.util.spec_from_file_location("trace_annotate", _MODULE_PATH)
trace_annotate = importlib.util.module_from_spec(_spec)
sys.modules["trace_annotate"] = trace_annotate
_spec.loader.exec_module(trace_annotate)


class TestClassifyBash(unittest.TestCase):
    def test_raw_pytest_is_flagged(self) -> None:
        flags = trace_annotate.classify_bash("python3 -m pytest tests/ -v")
        self.assertIn("AP-MAKE-BYPASS", flags)

    def test_raw_pip_install_of_lint_tools_is_flagged(self) -> None:
        flags = trace_annotate.classify_bash(
            "python3 -m pip install --user --quiet ruff pylint"
        )
        self.assertIn("AP-MAKE-BYPASS", flags)

    def test_venv_binary_call_is_flagged(self) -> None:
        flags = trace_annotate.classify_bash(
            "PYTHONPATH=. venv/bin/python3 -m pytest tests/test_x.py -v"
        )
        self.assertIn("AP-MAKE-BYPASS", flags)
        self.assertIn("AP-RAW-VENV", flags)

    def test_make_chat_mentioning_pylint_is_not_flagged(self) -> None:
        # Regression test for BUG-001.
        cmd = (
            'make chat MSG="ARCH.md complete. pylint 10/10, no duplication, '
            'no dead code. @Oracle *ora groom" PERSONA="Morpheus" '
            'CMD="lead handoff" TO="Oracle"'
        )
        flags = trace_annotate.classify_bash(cmd)
        self.assertNotIn("AP-MAKE-BYPASS", flags)

    def test_make_chat_mentioning_ruff_is_not_flagged(self) -> None:
        # Regression test for BUG-001.
        cmd = (
            'make chat MSG="Docs groomed: 2 process lessons '
            '(ruff/bandit config gaps)." '
            'PERSONA="Oracle" CMD="ora handoff" TO="Smith"'
        )
        flags = trace_annotate.classify_bash(cmd)
        self.assertNotIn("AP-MAKE-BYPASS", flags)

    def test_make_chat_with_actual_bypass_elsewhere_is_still_flagged(self) -> None:
        # A make chat command is never itself a bypass, but classify_bash
        # must still catch a genuine bypass in a compound command.
        cmd = 'pytest tests/; make chat MSG="done" PERSONA="Neo" CMD="swe handoff"'
        flags = trace_annotate.classify_bash(cmd)
        self.assertIn("AP-MAKE-BYPASS", flags)

    def test_piped_make_target_is_flagged(self) -> None:
        flags = trace_annotate.classify_bash("make setup 2>&1 | tail -60")
        self.assertIn("AP-MAKE-PIPE", flags)

    def test_piped_make_chat_is_not_flagged_as_pipe(self) -> None:
        flags = trace_annotate.classify_bash('make chat MSG="status" | tail -1')
        self.assertNotIn("AP-MAKE-PIPE", flags)

    def test_grep_for_source_symbols_is_flagged(self) -> None:
        flags = trace_annotate.classify_bash(
            'grep -n "def main\\|argparse" agents/tools/trace_annotate.py'
        )
        self.assertIn("AP-VIA-GREP", flags)

    def test_clean_command_has_no_flags(self) -> None:
        flags = trace_annotate.classify_bash("git status")
        self.assertEqual(flags, [])


if __name__ == "__main__":
    unittest.main()
