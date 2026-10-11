import unittest
from unittest.mock import patch

from cloudlayer import setup_tools


class SetupTests(unittest.TestCase):
    @patch("cloudlayer.setup_tools.change")
    @patch("cloudlayer.setup_tools.read_azure")
    def test_preview_extension_install_preserves_pending_provider(self, read, change):
        read.side_effect = [{"state": "Enabled"}, {"ml": "2.45.0"}, {"state": "Registering"},
                            {"ml": "2.45.0", "containerapp": "1.3.0b5"}, {"state": "Registered"}]
        report = setup_tools.collect()
        change.assert_called_once_with(
            ["extension", "add", "--name", "containerapp", "--version", "1.3.0b5",
             "--allow-preview", "true", "--yes"], report, "install_containerapp_extension")
        self.assertTrue(report["setup_ready"])

    @patch("cloudlayer.setup_tools.change")
    @patch("cloudlayer.setup_tools.read_azure")
    def test_status_does_not_change_cloud(self, read, change):
        read.side_effect = [{"state": "Enabled"}, {"ml": "2.45.0"}, {"state": "NotRegistered"}]
        report = setup_tools.collect(status_only=True)
        change.assert_not_called()
        self.assertFalse(report["setup_ready"])

    @patch("cloudlayer.setup_tools.change")
    @patch("cloudlayer.setup_tools.read_azure")
    def test_ready_setup_is_not_reinstalled(self, read, change):
        read.side_effect = [{"state": "Enabled"}, {"ml": "2.45.0", "containerapp": "1.3.0b5"},
                            {"state": "Registered"}, {"ml": "2.45.0", "containerapp": "1.3.0b5"},
                            {"state": "Registered"}]
        report = setup_tools.collect()
        change.assert_not_called()
        self.assertTrue(report["setup_ready"])

    @patch("cloudlayer.setup_tools.change")
    @patch("cloudlayer.setup_tools.read_azure")
    def test_pending_registration_is_not_restarted(self, read, change):
        read.side_effect = [{"state": "Enabled"}, {"containerapp": "1.3.0b5"}, {"state": "Registering"},
                            {"containerapp": "1.3.0b5"}, {"state": "Registering"}]
        report = setup_tools.collect()
        change.assert_not_called()
        self.assertFalse(report["setup_ready"])

    @patch("cloudlayer.setup_tools.change")
    @patch("cloudlayer.setup_tools.read_azure")
    def test_metadata_check_skips_slow_extension_list(self, read, change):
        read.side_effect = [{"state": "Enabled"}, {"containerapp": "1.3.0b5"}, {"state": "Registered"}]
        self.assertTrue(setup_tools.collect(status_only=True)["setup_ready"])
        self.assertEqual(read.call_args_list[1].args[0], ["version", "--query", "extensions"])
        for call in [read.call_args_list[0], read.call_args_list[2]]:
            self.assertIn("AZURE_EXTENSION_DIR", call.kwargs["env"])
        change.assert_not_called()


if __name__ == "__main__":
    unittest.main()
