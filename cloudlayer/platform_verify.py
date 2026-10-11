import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from cloudlayer.platform_preview import PROJECT, azure, check_group, plan_for


def has_role(rows, principal, scope, role):
    if not principal:
        return False
    return any(str(row.get("properties", {}).get("principalId", "")).lower() == principal.lower()
               and str(row["properties"].get("scope", "")).lower() == scope.lower()
               and str(row["properties"].get("roleDefinitionId", "")).rsplit("/", 1)[-1].lower() == role
               for row in rows)


def same_region(location, region):
    return isinstance(location, str) and location.lower().replace(" ", "") == region.lower().replace(" ", "")


def verify(root):
    config = json.loads((root / "configs/azure.json").read_text())
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "resources_changed": False,
              "platform_verified": False, "checks_failed": []}
    with tempfile.TemporaryDirectory(prefix="mlop-verify-") as directory:
        env = dict(os.environ, AZURE_EXTENSION_DIR=directory)
        account = azure(["account", "show", "--query", "{id:id,state:state}"], env)
        if account["state"] != "Enabled":
            raise ValueError("Subscription is not enabled.")
        plan = plan_for(account, config)
        report.update(plan)
        def run(args):
            return azure([*args, "--subscription", account["id"]], env)
        group = run(["group", "show", "--name", plan["resource_group"],
                     "--query", "{location:location,tags:tags}"])
        check_group(group, plan)
        report["cleanup_by_utc"] = group["tags"].get("removeAfter")
        base = f'https://management.azure.com/subscriptions/{account["id"]}/resourceGroups/{plan["resource_group"]}/providers/'
        suffix = plan["suffix"]
        specs = {
            "storage": ("Microsoft.Storage/storageAccounts", "stmloppj" + suffix, "2023-05-01"),
            "registry": ("Microsoft.ContainerRegistry/registries", "acrmloppj" + suffix, "2023-07-01"),
            "logs": ("Microsoft.OperationalInsights/workspaces", "log-mlop-pj-" + suffix, "2023-09-01"),
            "vault": ("Microsoft.KeyVault/vaults", "kv-mlop-pj-" + suffix, "2023-07-01"),
            "insights": ("Microsoft.Insights/components", "ai-mlop-pj-" + suffix, "2020-02-02"),
            "environment": ("Microsoft.App/managedEnvironments", "cae-mlop-pj-" + suffix, "2025-07-01"),
            "workspace": ("Microsoft.MachineLearningServices/workspaces", "ml-mlop-pj-" + suffix, "2026-03-01")}
        def read(item):
            label, (kind, name, version) = item
            value = run(["rest", "--method", "get", "--url", f"{base}{kind}/{name}?api-version={version}"])
            return label, value
        with ThreadPoolExecutor(max_workers=3) as pool:
            resources = dict(pool.map(read, specs.items()))
        checks = {}
        for label, resource in resources.items():
            state = resource.get("properties", {}).get("provisioningState")
            # Key Vault and Application Insights omit provisioningState in GET responses.
            checks[label] = (same_region(resource.get("location"), plan["region"])
                             and (resource.get("tags") or {}).get("project") == PROJECT
                             and (state == "Succeeded" or (label in {"vault", "insights"} and state is None)))
        workspace = resources["workspace"]
        principal = workspace.get("identity", {}).get("principalId")
        props = workspace["properties"]
        checks["workspace_identity"] = bool(principal) and workspace.get("identity", {}).get("type") == "SystemAssigned"
        checks["workspace_links"] = all(str(props.get(field, "")).lower() == resources[label]["id"].lower()
                                          for field, label in [("storageAccount", "storage"), ("keyVault", "vault"),
                                                               ("containerRegistry", "registry"), ("applicationInsights", "insights")])
        checks["identity_datastores"] = props.get("systemDatastoresAuthMode", "").lower() == "identity"
        checks["storage_shared_keys_disabled"] = resources["storage"]["properties"].get("allowSharedKeyAccess") is False
        checks["registry_admin_disabled"] = resources["registry"]["properties"].get("adminUserEnabled") is False
        checks["consumption_environment"] = any(p.get("workloadProfileType") == "Consumption"
                                                for p in resources["environment"]["properties"].get("workloadProfiles", []))
        container = run(["rest", "--method", "get", "--url",
                         f'{base}Microsoft.Storage/storageAccounts/stmloppj{suffix}/blobServices/default/containers/mlop-data?api-version=2023-05-01'])
        checks["private_data_container"] = container["properties"].get("publicAccess") == "None"
        roles = {"storage": "ba92f5b4-2d11-453d-a403-e96b0029c9fe",
                 "vault": "b86a8fe4-44ce-4948-aee5-eccb2c155cd7",
                 "registry": "7f951dda-4ed3-4680-a7ca-43fe172d538d"}
        for label, role in roles.items():
            scope = resources[label]["id"]
            url = f"https://management.azure.com{scope}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&$filter=atScope()"
            page = run(["rest", "--method", "get", "--url", url])
            if page.get("nextLink"):
                raise ValueError("Role results are paginated. Review before accepting verification.")
            checks[label + "_workspace_role"] = has_role(page["value"], principal, scope, role)
        report["checks"] = checks
        report["checks_failed"] = [name for name, passed in checks.items() if not passed]
        report["platform_verified"] = not report["checks_failed"]
        deployment = run(["deployment", "group", "show", "--resource-group", plan["resource_group"],
                          "--name", "mlop-platform", "--query", "{state:properties.provisioningState}"])
        report["deployment_state"] = deployment["state"]
        report["limits"] = ["Configuration and assigned roles are checked; data-plane operations and role propagation still need testing."]
    return report
