# Bugs — Judge Loop Findings

## BUG-001: `MAKE_BYPASS_RE` has no quote-awareness, false-flags `make chat` prose

**Found:** 2026-07-29, judge loop on session tool-use trace.
**Severity:** Low impact (cosmetic — inflates the trace report's flag count and misdirects attention), but a genuine detector defect.
**File:** `agents/tools/trace_annotate.py`, `MAKE_BYPASS_RE` (line ~128) / `classify_bash()` (line ~149).

**Repro:**
```
make chat MSG="ARCH.md complete. ... pylint 10/10, no duplication, no dead code. ..." PERSONA="Morpheus" ...
```
This command is a `make chat` invocation — already using make correctly. But `MAKE_BYPASS_RE` (`r'(?:^|\s|;|&&|\|\|)(?:\.venv/bin/|venv/bin/)?(pytest|ruff|pylint|mypy|black|isort|coverage|py\.test)\b'`) scans the **entire raw command string**, including the quoted `MSG="..."` value. Since the message text mentions "pylint" while reporting a lint result, the regex fires and the call is misclassified as `AP-MAKE-BYPASS` — a false positive.

**Confirmed instances this session:** trace entries `[241]` and `[261]` (both `make chat` calls whose message text mentioned `pylint`/`ruff` by name).

**Expected:** `classify_bash()` should not apply `MAKE_BYPASS_RE` against quoted string literals in a `make chat` command — only against the actual shell-executed portion.

**Fix:** Before running `MAKE_BYPASS_RE`, detect `make chat` commands and strip quoted string content first, so tool names mentioned in chat prose aren't matched. See Neo's fix in `agents/tools/trace_annotate.py` + new `tests/test_trace_annotate.py`.

---

## Process Findings (not code bugs, no fix needed — recorded for the record)

- **3 confirmed `AP-MAKE-BYPASS`** (raw `pytest`/`pip install` via Bash instead of `make test`/`make setup`) and **2 confirmed `AP-MAKE-PIPE`** (piped `make` output) occurred, all before the `make` skill was loaded this session (or, for one `AP-MAKE-BYPASS` instance, during single-file test iteration). Zero `AP-MAKE-PIPE` occurred after the skill was loaded — see Bob's recommendation in the handoff for a proactive-load nudge.
- **1 confirmed `AP-VIA-GREP`**: `via` (confirmed enabled) was bypassed in favor of `grep` to locate `add_argument`/`main()` in `agents/tools/trace_annotate.py`.
