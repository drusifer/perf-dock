"""Unit tests for perf_dock.ui_indicator's pure helper logic."""

import unittest

from perf_dock.ui_indicator import _format_freq


class TestFormatFreq(unittest.TestCase):
    def test_sub_ghz_formats_as_mhz(self) -> None:
        self.assertEqual(_format_freq(800000), "800MHz")

    def test_at_or_above_ghz_formats_as_ghz(self) -> None:
        self.assertEqual(_format_freq(2400000), "2.4GHz")

    def test_hardware_example_from_this_machine(self) -> None:
        self.assertEqual(_format_freq(710400), "710MHz")
        self.assertEqual(_format_freq(3417600), "3.4GHz")


if __name__ == "__main__":
    unittest.main()
