import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen


def fetch_prices(region, service, arm_sku=None):
    query = f"armRegionName eq '{region}' and serviceName eq '{service}' and priceType eq 'Consumption'"
    if arm_sku:
        query += f" and armSkuName eq '{arm_sku}'"
    url = "https://prices.azure.com/api/retail/prices?" + urlencode({"$filter": query})
    rows = []
    while url:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "prices.azure.com":
            raise ValueError("Unexpected price API page.")
        with urlopen(url, timeout=60) as response:
            page = json.load(response)
        rows.extend(page["Items"])
        url = page.get("NextPageLink")
    return rows


def select(rows, region, meter, unit, product=None):
    matches = [row for row in rows if row.get("armRegionName") == region
               and row.get("meterName") == meter and row.get("unitOfMeasure") == unit
               and row.get("currencyCode") == "USD" and row.get("type") == "Consumption"
               and row.get("tierMinimumUnits") == 0
               and (product is None or row.get("productName") == product)]
    if len(matches) != 1:
        raise ValueError(f"Expected one price for {meter}; got {len(matches)}. Review the API response.")
    row = matches[0]
    if row["retailPrice"] < 0:
        raise ValueError("Negative retail price.")
    return {key: row[key] for key in ["meterName", "unitOfMeasure", "retailPrice", "currencyCode",
                                     "productName", "skuName", "armRegionName", "effectiveStartDate"]}


def calculate(plan, rates, budget):
    seconds = plan["app_active_hours"] * 3600
    costs = {
        "acr_basic": plan["registry_days"] * rates["acr"]["retailPrice"],
        "training_linux_vm": plan["training_vm_hours"] * rates["vm"]["retailPrice"],
        "app_active_cpu": seconds * plan["app_cpu"] * rates["cpu"]["retailPrice"],
        "app_active_memory": seconds * plan["app_memory_gib"] * rates["memory"]["retailPrice"],
        "app_requests": plan["app_requests"] / 1_000_000 * rates["requests"]["retailPrice"],
    }
    subtotal = sum(costs.values()) * plan["planning_thb_per_usd"]
    total = subtotal + plan["other_services_reserve_thb"]
    return {"gross_usd_by_service": costs, "priced_subtotal_thb": round(subtotal, 2),
            "unpriced_services_reserve_thb": plan["other_services_reserve_thb"],
            "planned_total_thb": round(total, 2), "budget_thb_before_credits": budget,
            "within_planning_budget": total <= budget, "credits_and_free_grants_applied": False,
            "deploy_ready": False,
            "limits": ["This is a plan, not a bill or a spending cap.",
                       "Storage, logs, alerts, disks, network, and taxes are not priced; the reserve is an assumption.",
                       "Extra runtime or retained resources can exceed this plan.",
                       "Azure billing currency and exchange rate may differ.",
                       "Permissions and Azure ML/Container Apps quota still need review."]}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "configs/azure.json").read_text())
    plan = json.loads((root / "configs/cost-plan.json").read_text())
    region = config["candidate_region"]
    rows = {"acr": fetch_prices(region, "Container Registry"),
            "app": fetch_prices(region, "Azure Container Apps"),
            "vm": fetch_prices(region, "Virtual Machines", "Standard_DS2_v2")}
    rates = {
        "acr": select(rows["acr"], region, "Basic Registry Unit", "1/Day"),
        "vm": select(rows["vm"], region, "DS2 v2", "1 Hour", "Virtual Machines DSv2 Series"),
        "cpu": select(rows["app"], region, "Standard vCPU Active Usage", "1 Second"),
        "memory": select(rows["app"], region, "Standard Memory Active Usage", "1 GiB Second"),
        "requests": select(rows["app"], region, "Standard Requests", "1M"),
    }
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "region": region,
              "source": "https://prices.azure.com/api/retail/prices", "assumptions": plan,
              "rates": rates, **calculate(plan, rates, config["budget_thb_before_credits"])}
    (root / "reports/azure-retail-prices.json").write_text(json.dumps(rows, indent=2) + "\n")
    (root / "reports/azure-cost-plan.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
