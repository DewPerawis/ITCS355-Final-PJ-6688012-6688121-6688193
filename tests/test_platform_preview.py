import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from cloudlayer.platform_preview import PROJECT, check_recovery_resources, check_group, check_region_policy, plan_for, preview, refresh_region_reports, summarize_changes


class PreviewTests(unittest.TestCase):
    def test_names_are_repeatable_and_subscription_specific(self):
        config = {"candidate_region": "southeastasia", "budget_thb_before_credits": 150}
        account = {"id": "00000000-0000-0000-0000-000000000001"}
        plan = plan_for(account, config)
        self.assertEqual(plan, plan_for(account, config))
        other = plan_for({"id": "00000000-0000-0000-0000-000000000002"}, config)
        self.assertNotEqual(plan["resource_group"], other["resource_group"])
        self.assertNotIn(account["id"], str(plan))

    def test_existing_unrelated_group_is_rejected(self):
        with self.assertRaises(ValueError):
            check_group({"location": "southeastasia", "tags": {"project": "another-course"}},
                        {"region": "southeastasia"})
        check_group({"location": "southeastasia", "tags": {"project": PROJECT}}, {"region": "southeastasia"})

    def test_group_metadata_can_be_in_a_different_region(self):
        check_group({"location": "southeastasia", "tags": {"project": PROJECT}}, {"region": "centralindia"})

    def test_region_policy_rejects_denied_or_unknown_regions(self):
        assignments = [{"parameters": {"listOfAllowedLocations": {"value": ["centralindia"]}}}]
        self.assertEqual(check_region_policy(assignments, "centralindia"), ["centralindia"])
        for rows in [assignments, []]:
            with self.assertRaises(ValueError):
                check_region_policy(rows, "southeastasia")

    @patch("cloudlayer.platform_preview.subprocess.run")
    def test_stale_region_reports_are_refreshed(self, run):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            for name in ["azure-cost-plan.json", "azure-access-quota.json"]:
                (root / "reports" / name).write_text(json.dumps({"region": "southeastasia"}))
            def refresh(command, **kwargs):
                name = "azure-cost-plan.json" if command[-1] == "cloudlayer.cost_plan" else "azure-access-quota.json"
                (root / "reports" / name).write_text(json.dumps({"region": "centralindia"}))
                from types import SimpleNamespace
                return SimpleNamespace(returncode=0)
            run.side_effect = refresh
            refresh_region_reports(root, "centralindia")
            self.assertEqual(run.call_count, 2)
            refresh_region_reports(root, "centralindia")
            self.assertEqual(run.call_count, 2)

    def test_recovery_requires_owned_services_in_the_same_region(self):
        plan = {"suffix": "abc12345", "region": "centralindia"}
        names = [("Microsoft.Storage/storageAccounts", "stmloppj"),
                 ("Microsoft.ContainerRegistry/registries", "acrmloppj"),
                 ("Microsoft.OperationalInsights/workspaces", "log-mlop-pj-"),
                 ("Microsoft.Insights/components", "ai-mlop-pj-"),
                 ("Microsoft.App/managedEnvironments", "cae-mlop-pj-")]
        resources = [{"type": kind, "name": prefix + plan["suffix"],
                      "location": plan["region"], "tags": {"project": PROJECT}} for kind, prefix in names]
        check_recovery_resources(resources, plan)
        with self.assertRaises(ValueError):
            check_recovery_resources(resources[:-1], plan)
        resources[0]["tags"]["project"] = "another-project"
        with self.assertRaises(ValueError):
            check_recovery_resources(resources, plan)

    def test_preview_summary_hides_subscription_id(self):
        result = summarize_changes({"changes": [{"changeType": "Create", "resourceId":
            "/subscriptions/private-id/resourceGroups/test/providers/Microsoft.Storage/storageAccounts/test"}]})
        self.assertNotIn("private-id", str(result))
        self.assertEqual(result[0]["resource"], "Microsoft.Storage/storageAccounts/test")

    @patch("cloudlayer.platform_preview.azure")
    def test_preview_stops_before_writes_to_unrelated_group(self, azure):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "configs").mkdir()
            (root / "reports").mkdir()
            config = {"candidate_region": "southeastasia", "budget_thb_before_credits": 150}
            access = {"region": "southeastasia", "checks_failed": [], "control_plane_actions": {"write": True},
                      "training_quota_available": True, "container_apps_environment_slot_available": True}
            cost = {"within_planning_budget": True, "region": "southeastasia"}
            for file, value in [("configs/azure.json", config), ("reports/azure-access-quota.json", access),
                                ("reports/azure-cost-plan.json", cost)]:
                (root / file).write_text(json.dumps(value))
            azure.side_effect = [{"id": "00000000-0000-0000-0000-000000000001", "state": "Enabled"},
                                 [{"parameters": {"listOfAllowedLocations": {"value": ["southeastasia"]}}}],
                                 True, {"location": "southeastasia", "tags": {"project": "another-project"}}]
            with self.assertRaises(ValueError):
                preview(root, {})
            self.assertEqual(azure.call_count, 4)
            self.assertFalse(any("create" in call.args[0] for call in azure.call_args_list))


if __name__ == "__main__":
    unittest.main()
