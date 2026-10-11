import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cloudlayer.platform_deploy import deploy
from cloudlayer.platform_verify import has_role, same_region


class VerificationTests(unittest.TestCase):
    def test_role_must_match_principal_scope_and_definition(self):
        rows = [{"properties": {"principalId": "workspace-id", "scope": "/storage/project",
                                "roleDefinitionId": "/roles/blob-role"}}]
        self.assertTrue(has_role(rows, "workspace-id", "/storage/project", "blob-role"))
        self.assertFalse(has_role(rows, "another-id", "/storage/project", "blob-role"))
        self.assertFalse(has_role(rows, "workspace-id", "/storage/another", "blob-role"))
        self.assertFalse(has_role(rows, "workspace-id", "/storage/project", "another-role"))
        self.assertFalse(has_role(rows, None, "/storage/project", "blob-role"))

    def test_region_display_name_matches_canonical_name(self):
        self.assertTrue(same_region("Central India", "centralindia"))
        self.assertFalse(same_region("South India", "centralindia"))
        self.assertFalse(same_region(None, "centralindia"))

    @patch("cloudlayer.platform_deploy.azure")
    @patch("cloudlayer.platform_verify.verify")
    def test_duplicate_role_recovery_verifies_without_deployment(self, verify, azure):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            previous = {"paid_resources_may_exist": True, "errors": ["RoleAssignmentExists"],
                        "resource_group": "project-group", "region": "centralindia"}
            (root / "reports/azure-platform-deploy.json").write_text(json.dumps(previous))
            verify.return_value = {"resource_group": "project-group", "region": "centralindia",
                                   "platform_verified": True, "checks_failed": [], "deployment_state": "Failed"}
            report = {"apply_started": False}
            deploy(root, report)
            azure.assert_not_called()
            self.assertTrue(report["platform_created"])
            self.assertFalse(report["apply_started"])
            self.assertFalse(report["deployment_retried"])
            self.assertEqual(report["deployment_state"], "Failed")
            (root / "reports/azure-platform-deploy.json").write_text(json.dumps(report))
            deploy(root, {"apply_started": False})
            azure.assert_not_called()
            verify.return_value["platform_verified"] = False
            verify.return_value["checks_failed"] = ["storage_workspace_role"]
            with self.assertRaises(ValueError):
                deploy(root, {})
            azure.assert_not_called()


if __name__ == "__main__":
    unittest.main()
