"""Mutating actions and the single privilege-escalation path for perf-dock."""

import logging
import subprocess  # nosec B404
from dataclasses import dataclass

from perf_dock import cpufreq
from perf_dock.state import STATE_ERROR, classify_state

logger = logging.getLogger("perf_dock.controller")


@dataclass
class StateSnapshot:
    """A point-in-time read of the CPU frequency state."""

    state: str
    governor: str | None = None
    policy_min: int | None = None
    policy_max: int | None = None
    hw_min: int | None = None
    hw_max: int | None = None


class PerfDockController:
    """Wraps cpupower read/write ops behind a single privilege-escalation path."""

    def __init__(self) -> None:
        self._busy = False

    def is_busy(self) -> bool:
        """Returns True while a privileged frequency-set call is in flight."""
        return self._busy

    def get_details(self) -> StateSnapshot:
        """Reads the current governor/policy/hardware-limits and classifies state."""
        try:
            governor, policy_min, policy_max = cpufreq.get_policy()
            hw_min, hw_max = cpufreq.get_hwlimits()
        except cpufreq.CpuFreqUnavailableError:
            logger.exception("Failed to read cpufreq state")
            return StateSnapshot(state=STATE_ERROR)
        state = classify_state(governor, policy_min, policy_max, hw_min, hw_max)
        return StateSnapshot(
            state=state,
            governor=governor,
            policy_min=policy_min,
            policy_max=policy_max,
            hw_min=hw_min,
            hw_max=hw_max,
        )

    def is_available(self) -> bool:
        """Returns True if cpupower can be located on this system."""
        return cpufreq.is_available()

    def get_governors(self) -> list[str]:
        """Returns available governors, or an empty list if cpupower is unavailable."""
        try:
            return cpufreq.get_governors()
        except cpufreq.CpuFreqUnavailableError:
            return []

    def get_frequency_steps(self) -> list[int]:
        """Returns available hardware frequency steps (kHz), or [] if unavailable."""
        try:
            return cpufreq.get_frequency_steps()
        except cpufreq.CpuFreqUnavailableError:
            return []

    def set_governor(self, name: str) -> bool:
        """Applies a governor change to all related CPUs. False if cancelled/failed."""
        return self._run_privileged(["-g", name])

    def set_range(self, min_khz: int | None, max_khz: int | None) -> bool:
        """Sets min and/or max frequency; either bound may be None (no change)."""
        args: list[str] = []
        if min_khz is not None:
            args += ["-d", f"{min_khz}kHz"]
        if max_khz is not None:
            args += ["-u", f"{max_khz}kHz"]
        if not args:
            return True
        return self._run_privileged(args)

    def restore_default_range(self) -> bool:
        """Resets min/max frequency back to the hardware's full reported limits."""
        try:
            hw_min, hw_max = cpufreq.get_hwlimits()
        except cpufreq.CpuFreqUnavailableError:
            logger.exception("Cannot restore default range, cpupower unavailable")
            return False
        return self.set_range(hw_min, hw_max)

    def _run_privileged(self, args: list[str]) -> bool:
        try:
            cpupower_path = cpufreq.get_cpupower_path()
        except cpufreq.CpuFreqUnavailableError:
            logger.exception("cpupower unavailable, cannot apply change")
            return False

        self._busy = True
        try:
            command = ["pkexec", cpupower_path, "frequency-set", "-r", *args]
            result = subprocess.run(  # nosec B603 B607
                command, capture_output=True, text=True, check=False
            )
        except OSError:
            logger.exception("Failed to invoke pkexec")
            return False
        finally:
            self._busy = False

        if result.returncode != 0:
            logger.warning(
                "cpupower frequency-set was cancelled or failed (exit %s): %s",
                result.returncode,
                result.stderr.strip(),
            )
            return False
        return True
