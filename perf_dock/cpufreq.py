"""Low-level, read-only cpupower subprocess wrappers and output parsing.

Uses targeted `cpupower frequency-info` flags (-g, -l, -p) instead of the
full-text dump wherever a flag exists, since those outputs are far less
fragile to parse. `--hwlimits` (-l) prints clean kHz integers; the others
still need light regex extraction from human-readable sentences.
"""

import re
import shutil
import subprocess  # nosec B404

_CPUPOWER_PATH: str | None = None

_UNIT_TO_KHZ = {
    "hz": 0.001,
    "khz": 1,
    "mhz": 1000,
    "ghz": 1_000_000,
    "thz": 1_000_000_000,
}

_GOVERNORS_RE = re.compile(r"available cpufreq governors:\s*(.+)")
_HWLIMITS_LINE_RE = re.compile(r"^\s*(\d+)\s+(\d+)\s*$")
_POLICY_RANGE_RE = re.compile(
    r"within\s+([\d.]+)\s*(Hz|kHz|MHz|GHz|THz)\s+and\s+([\d.]+)\s*(Hz|kHz|MHz|GHz|THz)",
    re.IGNORECASE,
)
_POLICY_GOVERNOR_RE = re.compile(r'governor\s+"(\w+)"')
_STEPS_RE = re.compile(r"available frequency steps:\s*(.+)")
_STEP_TOKEN_RE = re.compile(r"([\d.]+)\s*(Hz|kHz|MHz|GHz|THz)", re.IGNORECASE)


class CpuFreqUnavailableError(RuntimeError):
    """Raised when cpupower is missing, fails, or its output can't be parsed."""


def _resolve_cpupower_path() -> str:
    global _CPUPOWER_PATH
    if _CPUPOWER_PATH is None:
        path = shutil.which("cpupower")
        if path is None:
            raise CpuFreqUnavailableError("cpupower executable not found on PATH")
        _CPUPOWER_PATH = path
    return _CPUPOWER_PATH


def get_cpupower_path() -> str:
    """Returns the absolute path to the cpupower binary, raising if missing."""
    return _resolve_cpupower_path()


def is_available() -> bool:
    """Returns True if cpupower can be located on PATH."""
    try:
        _resolve_cpupower_path()
    except CpuFreqUnavailableError:
        return False
    return True


def _run(extra_args: list[str]) -> str:
    path = _resolve_cpupower_path()
    try:
        result = subprocess.run(  # nosec B603
            [path, "frequency-info", *extra_args],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        raise CpuFreqUnavailableError(
            f"cpupower frequency-info {' '.join(extra_args)} failed: {exc}"
        ) from exc
    return result.stdout


def _to_khz(value: str, unit: str) -> int:
    return round(float(value) * _UNIT_TO_KHZ[unit.lower()])


def get_governors() -> list[str]:
    """Returns the list of cpufreq governors this hardware/driver supports."""
    output = _run(["-g"])
    match = _GOVERNORS_RE.search(output)
    if not match:
        raise CpuFreqUnavailableError(f"could not parse governors from: {output!r}")
    return match.group(1).split()


def get_hwlimits() -> tuple[int, int]:
    """Returns (min_khz, max_khz) — the hardware's full allowed frequency range."""
    output = _run(["-l"])
    for line in output.splitlines():
        match = _HWLIMITS_LINE_RE.match(line)
        if match:
            return int(match.group(1)), int(match.group(2))
    raise CpuFreqUnavailableError(f"could not parse hwlimits from: {output!r}")


def get_policy() -> tuple[str, int, int]:
    """Returns (governor, policy_min_khz, policy_max_khz) — the active policy."""
    output = _run(["-p"])
    range_match = _POLICY_RANGE_RE.search(output)
    governor_match = _POLICY_GOVERNOR_RE.search(output)
    if not range_match or not governor_match:
        raise CpuFreqUnavailableError(f"could not parse policy from: {output!r}")
    policy_min = _to_khz(range_match.group(1), range_match.group(2))
    policy_max = _to_khz(range_match.group(3), range_match.group(4))
    return governor_match.group(1), policy_min, policy_max


def get_frequency_steps() -> list[int]:
    """Returns the sorted list of discrete frequency steps (kHz) hardware supports."""
    output = _run([])
    match = _STEPS_RE.search(output)
    if not match:
        raise CpuFreqUnavailableError(f"could not parse freq steps from: {output!r}")
    steps = {
        _to_khz(value, unit) for value, unit in _STEP_TOKEN_RE.findall(match.group(1))
    }
    return sorted(steps)
