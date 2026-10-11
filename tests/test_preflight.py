import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cloudlayer.preflight import collect, read_azure


class PreflightTests(unittest.TestCase):
    def collect_with_quota(self, quota):
        def response(args, failed, label):
            if args[:2] == ["account", "show"]:
                return {"state": "Enabled"}
            if args[:2] == ["account", "list-locations"]:
                return [{"name": "southeastasia", "displayName": "Southeast Asia"}]
            if args[:2] == ["provider", "show"]:
                return {"state": "Registered", "types": []}
            if args[:2] == ["vm", "list-usage"]:
                return quota
            if args[:2] == ["extension", "list"]:
                return []
            raise AssertionError("Unexpected Azure command.")

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "configs").mkdir()
            (root / "configs/azure.json").write_text(json.dumps(
                {"candidate_region": "southeastasia", "budget_thb_before_credits": 150}))
            with patch("cloudlayer.preflight.shutil.which", return_value="az"), \
                    patch("cloudlayer.preflight.read_azure", side_effect=response):
                return collect(root)

    def test_cli_string_and_integer_quotas(self):
        report = self.collect_with_quota([
            {"name": "cores", "limit": "20", "current": "2"},
            {"name": "standardDSv2Family", "limit": 8, "current": 0}])
        self.assertEqual(report["vm_quota"][0], {"name": "cores", "limit": 20, "current": 2, "remaining": 18})
        self.assertEqual(report["vm_quota"][1]["remaining"], 8)
        self.assertEqual(report["checks_failed"], [])
        self.assertFalse(report["deploy_ready"])

    def test_unknown_quota_stays_unknown(self):
        report = self.collect_with_quota([
            {"name": "cores", "limit": "N/A", "current": "0"},
            {"name": None, "limit": "4", "current": "0"}])
        self.assertEqual(report["checks_failed"], ["vm_quota_values"])
        self.assertIsNone(report["vm_quota"][0]["remaining"])
        self.assertFalse(report["deploy_ready"])

    def test_failed_cli_does_not_print_account_details(self):
        result = SimpleNamespace(returncode=1, stdout="", stderr="private account details")
        captured, failed = io.StringIO(), []
        with patch("cloudlayer.preflight.subprocess.run", return_value=result), \
                redirect_stdout(captured), redirect_stderr(captured):
            self.assertIsNone(read_azure(["account", "show"], failed, "account_state"))
        self.assertEqual(failed, ["account_state"])
        self.assertEqual(captured.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
