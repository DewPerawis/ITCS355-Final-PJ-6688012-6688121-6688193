import unittest

from cloudlayer.access_check import allows, available, quota_rows


class AccessTests(unittest.TestCase):
    def test_not_actions_apply_within_each_permission(self):
        permissions = [{"actions": ["*"], "notActions": ["Microsoft.App/*"]}]
        self.assertFalse(allows(permissions, "Microsoft.App/containerApps/write"))
        permissions.append({"actions": ["Microsoft.App/containerApps/write"], "notActions": []})
        self.assertTrue(allows(permissions, "Microsoft.App/containerApps/write"))

    def test_dedicated_quota_does_not_use_low_priority_row(self):
        rows = [{"name": {"value": "standardDSv2Family", "localizedValue": "DSv2 Dedicated vCPUs"},
                 "limit": "6", "currentValue": "0"},
                {"name": {"value": "standardDSv2Family", "localizedValue": "DSv2 LowPriority vCPUs"},
                 "limit": -1, "currentValue": 0}]
        failed = []
        result = quota_rows(rows, failed, "azure_ml", aml=True)
        self.assertEqual(failed, [])
        self.assertTrue(available(result, "standardDSv2Family", 2))
        self.assertFalse(available(result, "standardDSv2Family", 8))

    def test_unknown_quota_does_not_pass(self):
        failed = []
        rows = [{"name": {"value": "ManagedEnvironmentCount"}, "limit": "unknown", "currentValue": 0}]
        result = quota_rows(rows, failed, "container_apps")
        self.assertFalse(available(result, "ManagedEnvironmentCount", 1))
        self.assertEqual(failed, ["container_apps_values"])


if __name__ == "__main__":
    unittest.main()
