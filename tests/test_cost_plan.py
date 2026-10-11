import unittest

from cloudlayer.cost_plan import calculate, select


class CostTests(unittest.TestCase):
    def test_ambiguous_price_is_rejected(self):
        row = {"armRegionName": "southeastasia", "meterName": "Basic Registry Unit",
               "unitOfMeasure": "1/Day", "currencyCode": "USD", "type": "Consumption",
               "tierMinimumUnits": 0}
        with self.assertRaises(ValueError):
            select([row, row], "southeastasia", "Basic Registry Unit", "1/Day")

    def test_gross_cost_does_not_assume_free_grants(self):
        plan = {"app_active_hours": 2, "registry_days": 2, "training_vm_hours": 1,
                "app_cpu": 1, "app_memory_gib": 2, "app_requests": 10000,
                "planning_thb_per_usd": 40, "other_services_reserve_thb": 60}
        rates = {name: {"retailPrice": value} for name, value in {
            "acr": 0.1666, "vm": 0.158, "cpu": 0.000034, "memory": 0.000004, "requests": 0.4}.items()}
        report = calculate(plan, rates, 150)
        self.assertAlmostEqual(report["planned_total_thb"], 91.9)
        self.assertFalse(report["credits_and_free_grants_applied"])
        self.assertFalse(report["deploy_ready"])
        self.assertFalse(calculate(plan, rates, 80)["within_planning_budget"])


if __name__ == "__main__":
    unittest.main()
