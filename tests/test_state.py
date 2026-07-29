"""Unit tests for perf_dock.state (pure classification logic, no mocks needed)."""

import unittest

from perf_dock.state import (
    STATE_BALANCED,
    STATE_CUSTOM,
    STATE_PERFORMANCE,
    STATE_POWERSAVE,
    classify_state,
)


class TestClassifyState(unittest.TestCase):
    def test_performance_governor_full_range(self) -> None:
        state = classify_state("performance", 710400, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_PERFORMANCE)

    def test_powersave_governor_full_range(self) -> None:
        state = classify_state("powersave", 710400, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_POWERSAVE)

    def test_ondemand_governor_maps_to_balanced(self) -> None:
        state = classify_state("ondemand", 710400, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_BALANCED)

    def test_schedutil_governor_maps_to_balanced(self) -> None:
        state = classify_state("schedutil", 710400, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_BALANCED)

    def test_unknown_governor_defaults_to_balanced(self) -> None:
        state = classify_state("conservative", 710400, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_BALANCED)

    def test_narrowed_range_is_custom_even_with_performance_governor(self) -> None:
        state = classify_state("performance", 1000000, 2000000, 710400, 3417600)
        self.assertEqual(state, STATE_CUSTOM)

    def test_narrowed_min_only_is_custom(self) -> None:
        state = classify_state("ondemand", 1000000, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_CUSTOM)

    def test_narrowed_max_only_is_custom(self) -> None:
        state = classify_state("ondemand", 710400, 2000000, 710400, 3417600)
        self.assertEqual(state, STATE_CUSTOM)

    def test_real_hardware_rounding_noise_is_not_custom(self) -> None:
        # Regression test: on real hardware, `cpupower -p` prints rounded
        # human units ("710 MHz", "3.42 GHz") while `-l --hwlimits` prints
        # exact kHz, so policy_min/max never exactly equal hw_min/max even
        # at the full range. Observed live on this machine.
        state = classify_state("performance", 710000, 3420000, 710400, 3417600)
        self.assertEqual(state, STATE_PERFORMANCE)

    def test_small_deviation_within_tolerance_is_not_custom(self) -> None:
        state = classify_state(
            "ondemand", 710400 + 4000, 3417600 - 4000, 710400, 3417600
        )
        self.assertEqual(state, STATE_BALANCED)

    def test_deviation_beyond_tolerance_is_custom(self) -> None:
        state = classify_state("ondemand", 710400 + 6000, 3417600, 710400, 3417600)
        self.assertEqual(state, STATE_CUSTOM)


if __name__ == "__main__":
    unittest.main()
