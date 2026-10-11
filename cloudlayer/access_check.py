import fnmatch
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

from cloudlayer.preflight import quota_count, read_azure


def allows(permissions, action):
    action = action.lower()
    return any(any(fnmatch.fnmatchcase(action, p.lower()) for p in row.get("actions", []))
               and not any(fnmatch.fnmatchcase(action, p.lower()) for p in row.get("notActions", []))
               for row in permissions)


def read_pages(url, failed, label, env):
    rows = []
    visited = set()
    while url:
        if url in visited or urlparse(url).hostname != "management.azure.com" or not url.startswith("https://"):
            failed.append(label + "_pagination")
            return None
        visited.add(url)
        page = read_azure(["rest", "--method", "get", "--url", url], failed, label, env=env)
        if not isinstance(page, dict) or not isinstance(page.get("value"), list):
            if label not in failed:
                failed.append(label)
            return None
        rows.extend(page["value"])
        url = page.get("nextLink")
    return rows


def quota_rows(rows, failed, label, aml=False):
    selected = []
    for row in rows or []:
        name = row.get("name", {})
        if not isinstance(name, dict):
            failed.append(label + "_shape")
            continue
        value, display = name.get("value", ""), name.get("localizedValue", "")
        if aml and not (value in {"TotalClusters", "TotalDedicatedCores"}
                        or (value.lower() == "standarddsv2family" and "dedicated" in display.lower())):
            continue
        entry = {"name": value, "description": display}
        try:
            limit, current = quota_count(row["limit"]), quota_count(row["currentValue"])
            entry.update(limit=limit, current=current, remaining=limit - current)
        except (KeyError, ValueError, TypeError):
            entry.update(limit=None, current=None, remaining=None)
            failed.append(label + "_values")
        selected.append(entry)
    return selected


def available(rows, name, amount):
    matches = [r for r in rows if r["name"].lower() == name.lower()]
    return len(matches) == 1 and matches[0]["remaining"] is not None and matches[0]["remaining"] >= amount


def collect(root):
    config = json.loads((root / "configs/azure.json").read_text())
    failed = []
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "region": config["candidate_region"],
              "checks_failed": failed, "resources_created": False, "deploy_ready": False}
    with tempfile.TemporaryDirectory(prefix="mlop-azure-access-") as directory:
        env = os.environ.copy()
        env["AZURE_EXTENSION_DIR"] = directory
        account = read_azure(["account", "show", "--query", "{id:id,state:state}"], failed, "account", env=env)
        if not account or account.get("state") != "Enabled":
            failed.append("subscription_not_enabled")
            return report
        subscription = str(UUID(account["id"]))
        base = f"https://management.azure.com/subscriptions/{subscription}/providers/"
        region = config["candidate_region"]
        permissions = read_pages(base + "Microsoft.Authorization/permissions?api-version=2022-04-01",
                                 failed, "permissions", env)
        actions = ["Microsoft.Resources/subscriptions/resourceGroups/write", "Microsoft.Storage/storageAccounts/write",
                   "Microsoft.ContainerRegistry/registries/write", "Microsoft.App/managedEnvironments/write",
                   "Microsoft.App/containerApps/write", "Microsoft.MachineLearningServices/workspaces/write",
                   "Microsoft.OperationalInsights/workspaces/write", "Microsoft.Insights/components/write",
                   "Microsoft.KeyVault/vaults/write", "Microsoft.Authorization/roleAssignments/write"]
        report["control_plane_actions"] = {action: allows(permissions, action) if permissions is not None else None
                                           for action in actions}
        aml = read_pages(base + f"Microsoft.MachineLearningServices/locations/{region}/usages?api-version=2026-03-01",
                         failed, "azure_ml_usage", env)
        app = read_pages(base + f"Microsoft.App/locations/{region}/usages?api-version=2025-07-01",
                         failed, "container_apps_usage", env)
        report["azure_ml_quota"] = quota_rows(aml, failed, "azure_ml", aml=True)
        report["container_apps_quota"] = quota_rows(app, failed, "container_apps")
        report["training_quota_available"] = (available(report["azure_ml_quota"], "TotalClusters", 1)
                                               and available(report["azure_ml_quota"], "TotalDedicatedCores", 2)
                                               and available(report["azure_ml_quota"], "standardDSv2Family", 2))
        report["container_apps_environment_slot_available"] = available(report["container_apps_quota"],
                                                                         "ManagedEnvironmentCount", 1)
    report["limits"] = ["Control-plane permissions do not prove data access or bypass policies and locks.",
                        "Listed quota does not guarantee VM capacity.",
                        "Container Apps environment CPU quota must be checked after creating the environment.",
                        "The cost plan has unpriced services and assumed exchange rate/reserve."]
    report["next"] = "Review this report, then prepare a small resource group and Azure setup."
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = collect(root)
    (root / "reports/azure-access-quota.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
