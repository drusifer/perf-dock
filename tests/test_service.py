"""Contract tests for the Shell extension's transport-independent service."""

import unittest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from perf_dock.controller import PerfDockController, StateSnapshot
from perf_dock.service import INTERFACE_XML_PATH, ControlServiceCore, snapshot_payload
from perf_dock.state import STATE_PERFORMANCE


class TestControlServiceCore(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = MagicMock(spec=PerfDockController)
        self.controller.is_busy.return_value = False
        self.controller.get_governors.return_value = ["powersave", "performance"]
        self.core = ControlServiceCore(self.controller)

    def test_snapshot_payload_is_stable_and_null_free(self) -> None:
        payload = snapshot_payload(
            StateSnapshot(
                state=STATE_PERFORMANCE,
                governor="performance",
                policy_min=710400,
                policy_max=3417600,
            )
        )
        self.assertEqual(payload["governor"], "performance")
        self.assertEqual(payload["hw_min"], 0)
        self.assertFalse(payload["busy"])

    def test_rejects_governor_not_reported_by_hardware(self) -> None:
        accepted, message = self.core.set_governor("userspace")
        self.assertFalse(accepted)
        self.assertIn("not available", message)
        self.controller.set_governor.assert_not_called()

    def test_applies_available_governor(self) -> None:
        self.controller.set_governor.return_value = True
        self.assertEqual(self.core.set_governor("performance"), (True, ""))
        self.controller.set_governor.assert_called_once_with("performance")

    def test_reports_cancelled_or_failed_change(self) -> None:
        self.controller.set_governor.return_value = False
        accepted, message = self.core.set_governor("performance")
        self.assertFalse(accepted)
        self.assertIn("cancelled or failed", message)

    def test_busy_service_rejects_duplicate_change(self) -> None:
        self.controller.is_busy.return_value = True
        accepted, message = self.core.set_governor("performance")
        self.assertFalse(accepted)
        self.assertIn("already in progress", message)

    def test_range_dialog_reports_unavailable_without_ui(self) -> None:
        accepted, message = self.core.show_range()
        self.assertFalse(accepted)
        self.assertIn("unavailable", message)

    def test_range_dialog_callback_is_used(self) -> None:
        callback = MagicMock()
        core = ControlServiceCore(self.controller, show_range_dialog=callback)
        self.assertEqual(core.show_range(), (True, ""))
        callback.assert_called_once_with()

    def test_contract_is_valid_and_versioned(self) -> None:
        root = ET.parse(INTERFACE_XML_PATH).getroot()  # noqa: S314
        interface = root.find("interface")
        self.assertEqual(interface.get("name"), "io.github.perf_dock.Control1")
        methods = {method.get("name") for method in interface.findall("method")}
        self.assertEqual(
            methods,
            {
                "GetSnapshot",
                "GetGovernors",
                "SetGovernor",
                "ShowRangeDialog",
                "RestoreDefaultRange",
                "Refresh",
                "Quit",
            },
        )

    def test_extension_and_backend_share_the_same_contract(self) -> None:
        extension_contract = (
            INTERFACE_XML_PATH.parents[2]
            / "shell-extension"
            / "dbus"
            / INTERFACE_XML_PATH.name
        )
        backend = ET.canonicalize(from_file=INTERFACE_XML_PATH, strip_text=True)
        frontend = ET.canonicalize(from_file=extension_contract, strip_text=True)
        self.assertEqual(frontend, backend)


if __name__ == "__main__":
    unittest.main()
