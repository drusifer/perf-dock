# Project Lessons Learned

This file contains critical lessons and rules derived from past errors, technical discoveries, and architectural decisions. All agents MUST review this file before starting new implementation or architectural tasks.

---

## [2026-05-06] Transition to Artifact-Based Verification

> **Tags:** #Process #Oracle #Neo

### Context
Agents were previously instructed to consult the Oracle persona via chat for historical context and decisions. This often resulted in chat messages that were never picked up or processed by the intended persona.

### The Issue
Chat-based consultation is asynchronous and unreliable for immediate blocking needs. Agents would wait for a response that might not come, stalling progress.

### The Solution
Replaced "Oracle First" chat-based consultation with "Artifacts First" document-based verification. Agents now read consolidated logs and sprint plans directly.

### The Rule (The "Lesson")
DO NOT consult the Oracle via chat (`@Oracle *ora ask ...`) for routine historical or context checks. Instead, read the following artifacts in order: 1) Mouse's sprint plan (`agents/mouse.docs/`), 2) Oracle's `lessons.md` and `memory.md`, and 3) the recent `CHAT.md` history.

### References
- **Files:** `agents/*/SKILL.md`, `agents/oracle.docs/lessons.md`

---

## [2026-07-29] Makefile.prj targets need a stub in the root Makefile too

> **Tags:** #Process #Neo #Make

### Context
Neo tried to run `make setup`/`make lint` (defined in `Makefile.prj`) directly and got "No rule to make target" even though the root `Makefile` does `-include Makefile.prj`.

### The Issue
The root Makefile only exposes `Makefile.prj` targets inside its `ifdef MKF_ACTIVE` re-invocation layer. The top-level `else` block (the one a plain `make <target>` actually hits) only defines stubs for a fixed list of targets (`help`, `chat`, `test`, `via_index`, `install_bob`, etc.) that route through `agents/tools/mkf.py`. Any Makefile.prj target without a matching stub in that `else` block is simply invisible at the top level.

### The Rule (The "Lesson")
When adding a new project-specific target to `Makefile.prj` (`setup`, `run`, `lint`, `format`, `clean`, `install`, `install-system-deps`, etc.), you MUST also add a matching one-line stub to the root `Makefile`'s `else` block (`<target>: ## desc\n\t@./agents/tools/mkf.py $(V) $@`) and add it to that block's `.PHONY` line. See `.claude/skills/make/SKILL.md` → "Adding a new target" for the exact pattern. Both files must be updated or the target either doesn't exist (`Makefile` missing the stub) or silently bypasses mkf output-capture (`Makefile.prj` missing the recipe).

### References
- **Files:** `Makefile`, `Makefile.prj`, `.claude/skills/make/SKILL.md`

---

## [2026-07-29] ruff/bandit config additions needed beyond nerd-dock's baseline

> **Tags:** #Process #Neo #Lint

### Context
perf-dock reused nerd-dock's `pyproject.toml` ruff config as a starting point, but `make lint` still failed on rules nerd-dock's codebase never triggered.

### The Issue
- `S607` (partial executable path) fires for `pkexec`/`systemctl`/`cpupower` calls that intentionally rely on `$PATH` resolution — nerd-dock's ignore list only had `S603`.
- `PT019` fires on any test parameter starting with `_` that ruff assumes is an unused pytest fixture — but this codebase's tests use `unittest.mock.patch` decorators (not real pytest fixtures) with intentionally-unused, underscore-prefixed mock args. This is a false positive for that style, not a real issue.
- Bandit itself (not ruff) still flags `B404`/`B603`/`B607` per subprocess call/import even when ruff's `S`-prefixed equivalents are ignored — bandit needs its own inline `# nosec B404`/`# nosec B603 B607` comments, matching nerd-dock's existing pattern (nerd-dock has `# nosec B404`/`# nosec B603` in `controller.py`).

### The Rule (The "Lesson")
For any new bob-protocol Python project that shells out via `subprocess` with partial paths (systemctl, pkexec, or any PATH-resolved binary) and tests it with `unittest.mock.patch`: add `S607` and `PT019` to `pyproject.toml`'s ruff ignore list up front, and add bandit's inline `# nosec BNNN` comments on every subprocess import and call site — don't wait to discover these one lint run at a time.

### References
- **Files:** `pyproject.toml`, `perf_dock/controller.py`, `perf_dock/cpufreq.py`, `perf_dock/ppd_check.py`

---

## [2026-07-29] Mocked unit tests validated a self-consistent bug — only real-hardware testing caught it

> **Tags:** #Process #Smith #Trin #Testing

### Context
`state.classify_state()` compared `cpupower -p` policy output against `cpupower -l --hwlimits` output for exact equality to detect a user-pinned custom range. 43 mocked unit tests passed. Smith then ran the actual controller against this machine's real `cpupower` and got `CUSTOM` instead of the correct `PERFORMANCE`.

### The Issue
`cpupower -p` prints frequencies rounded to human units ("710 MHz", "3.42 GHz"), while `-l` prints exact kHz integers (710400, 3417600). The two will almost never be bit-for-bit equal on real hardware, even when the CPU is at its full, un-pinned range. The mocked tests never caught this because the mock's hand-written policy/hwlimits values were always constructed to match each other exactly — the tests validated the code's own assumptions, not reality.

### The Rule (The "Lesson")
When a component wraps a CLI tool's output, mocked tests alone are not sufficient sign-off — at least one pass must run the real subprocess against real (or captured real) output before calling a UAT/e2e gate complete. This is why the Sprint Bloop's Smith `*user test` step is a distinct, mandatory gate from Trin's `*qa test`: Trin's mocks prove the code does what the mocks say; Smith's real run proves the mocks matched reality.

### The Fix
`classify_state()` now uses a tolerance-based comparison (`_RANGE_TOLERANCE_KHZ = 5000`) instead of exact equality — real custom-pinned ranges differ by a full hardware frequency step (tens to hundreds of MHz), far more than cpupower's rounding noise.

### References
- **Files:** `perf_dock/state.py`, `tests/test_state.py`
