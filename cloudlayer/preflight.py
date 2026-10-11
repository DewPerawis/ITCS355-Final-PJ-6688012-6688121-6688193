import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def read_azure(args, failed, label, env=None):
    try:
        result = subprocess.run(["az", *args, "--only-show-errors", "-o", "json"],
                                capture_output=True, text=True, timeout=60, env=env)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    # Raw CLI errors can contain account details. Keep only the check name.
    failed.append(label)
    return None


def quota_count(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError("Quota must be an integer or integer string.")
    count = int(value)
    if count < 0:
        raise ValueError("Quota must not be negative.")
    return count


def collect(root):
    config = json.loads((root / "configs/azure.json").read_text())
    region = config["candidate_region"]
    failed = []
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "candidate_region": region,
              "budget_thb_before_credits": config["budget_thb_before_credits"],
              "resources_created": False, "provider_registration_changed": False,
              "permissions_reviewed": False, "cost_reviewed": False,
              "container_apps_quota_reviewed": False, "azure_ml_quota_reviewed": False,
              "deploy_ready": False, "checks_failed": failed}
    if not shutil.which("az"):
        failed.append("azure_cli_missing")
        return report
    account = read_azure(["account", "show", "--query", "{state:state}"], failed, "account_state")
    report["subscription_enabled"] = account is not None and account.get("state") == "Enabled"
    if not report["subscription_enabled"]:
        return report
    locations = read_azure(["account", "list-locations", "--query", "[].{name:name,displayName:displayName}"],
                           failed, "region_list")
    location = next((row for row in locations or [] if row["name"] == region), None)
    report["region_listed_for_subscription"] = location is not None
    display = location["displayName"] if location else ""
    providers = {"Microsoft.App": "managedEnvironments", "Microsoft.ContainerRegistry": "registries",
                 "Microsoft.MachineLearningServices": "workspaces", "Microsoft.Storage": "storageAccounts",
                 "Microsoft.OperationalInsights": "workspaces", "Microsoft.Insights": "components",
                 "Microsoft.KeyVault": "vaults"}
    report["providers"] = {}
    for namespace, resource_type in providers.items():
        data = read_azure(["provider", "show", "--namespace", namespace,
                           "--query", "{state:registrationState,types:resourceTypes[].{name:resourceType,locations:locations}}"],
                          failed, namespace)
        entry = next((row for row in (data or {}).get("types", []) if row["name"] == resource_type), None)
        supported = (entry or {}).get("locations", []) or []
        report["providers"][namespace] = {"registration_state": (data or {}).get("state"),
                                         "resource_type": resource_type,
                                         "region_listed": any(value.lower() in {display.lower(), region.lower()}
                                                              for value in supported)}
    usages = read_azure(["vm", "list-usage", "--location", region,
                        "--query", "[].{name:name.value,limit:limit,current:currentValue}"], failed, "vm_quota")
    report["vm_quota"] = []
    for row in usages or []:
        name = row.get("name")
        if not isinstance(name, str) or name.lower() not in {"cores", "standarddsv2family"}:
            continue
        try:
            limit, current = quota_count(row["limit"]), quota_count(row["current"])
        except (KeyError, TypeError, ValueError):
            failed.append("vm_quota_values")
            report["vm_quota"].append({"name": name, "limit": None, "current": None, "remaining": None})
            continue
        report["vm_quota"].append({"name": name, "limit": limit, "current": current,
                                   "remaining": limit - current})
    report["quota_note"] = "VM quota only; this does not prove Azure ML compute or Container Apps capacity."
    report["extensions"] = read_azure(["extension", "list", "--query", "[].name"], failed, "extension_list")
    report["next"] = "Review missing providers, permissions, service quotas, current prices, and cleanup timing."
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = collect(root)
    (root / "reports/azure-preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
