"""Pure CPU performance state classification logic (no I/O, no subprocess calls)."""

STATE_PERFORMANCE = "PERFORMANCE"
STATE_POWERSAVE = "POWERSAVE"
STATE_BALANCED = "BALANCED"
STATE_CUSTOM = "CUSTOM"
STATE_ERROR = "ERROR"

_GOVERNOR_STATE_MAP = {
    "performance": STATE_PERFORMANCE,
    "powersave": STATE_POWERSAVE,
}

# cpupower's `-p` policy output rounds to human units ("710 MHz", "3.42 GHz")
# while `-l --hwlimits` prints exact kHz. On real hardware those two rarely
# match bit-for-bit even at the full range (e.g. 710000 vs 710400 kHz), so an
# exact-equality comparison misclassifies the common case as CUSTOM. A real
# pinned range differs by at least one hardware frequency step (tens to
# hundreds of MHz), far larger than this rounding noise.
_RANGE_TOLERANCE_KHZ = 5000


def classify_state(
    governor: str, policy_min: int, policy_max: int, hw_min: int, hw_max: int
) -> str:
    """Classifies the current CPU frequency state from governor and range data.

    A policy range narrower than the hardware's full range (beyond normal
    rounding noise) means the user has pinned a custom range, which takes
    precedence over the governor's name.
    """
    if (
        abs(policy_min - hw_min) > _RANGE_TOLERANCE_KHZ
        or abs(policy_max - hw_max) > _RANGE_TOLERANCE_KHZ
    ):
        return STATE_CUSTOM
    return _GOVERNOR_STATE_MAP.get(governor, STATE_BALANCED)
