import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID


PROJECT = "mlop-pj-6688012"


def azure(args, env):
    result = subprocess.run(["az", *args, "--only-show-errors", "-o", "json"],
                            capture_output=True, text=True, env=env, timeout=600)
    if result.returncode:
        matches = re.findall(r'\(([A-Za-z][A-Za-z0-9.]+)\)|"code"\s*:\s*"([A-Za-z][A-Za-z0-9.]+)"|Code:\s*([A-Za-z][A-Za-z0-9.]+)', result.stderr)
        codes = [value for match in matches for value in match if value]
        raise RuntimeError("Azure CLI failed: " + (", ".join(dict.fromkeys(codes)) or "CLIError"))
    return json.loads(result.stdout) if result.stdout.strip() else None


def plan_for(account, config):
    subscription = str(UUID(account["id"]))
    suffix = hashlib.sha256((PROJECT + subscription).encode()).hexdigest()[:8]
    return {"resource_group": f"rg-mlop-pj-{suffix}", "region": config["candidate_region"],
            "suffix": suffix, "project_tag": PROJECT,
            "budget_thb_before_credits": config["budget_thb_before_credits"]}


def check_group(group, plan):
    if not group.get("location") or (group.get("tags") or {}).get("project") != PROJECT:
        raise ValueError("Existing resource group has different ownership or missing location. Stop for review.")


def check_region_policy(assignments, region):
    lists = [row["parameters"]["listOfAllowedLocations"]["value"] for row in assignments
             if "listOfAllowedLocations" in (row.get("parameters") or {})
             and row.get("enforcementMode") != "DoNotEnforce"]
    if not lists or any(not isinstance(values, list) or region not in values for values in lists):
        raise ValueError("Region is not confirmed by the allowed-location policies. Review the region first.")
    return sorted(set.intersection(*(set(values) for values in lists)))


def summarize_changes(data):
    return [{"change": row["changeType"],
             "resource": (row["resourceId"].split("/providers/", 1)[1]
                          if "/providers/" in row["resourceId"] else row["resourceId"].rsplit("/", 1)[-1])}
            for row in data.get("changes", [])]


def template_for(root, config):
    name = config.get("platform_template", "infra/platform.json")
    if name not in {"infra/platform.json", "infra/platform-recovery.json"}:
        raise ValueError("Unexpected platform template.")
    return root / name


def check_recovery_resources(resources, plan):
    required = {"Microsoft.Storage/storageAccounts": "stmloppj",
                "Microsoft.ContainerRegistry/registries": "acrmloppj",
                "Microsoft.OperationalInsights/workspaces": "log-mlop-pj-",
                "Microsoft.Insights/components": "ai-mlop-pj-",
                "Microsoft.App/managedEnvironments": "cae-mlop-pj-"}
    for kind, prefix in required.items():
        matches = [r for r in resources if r["type"] == kind and r["name"] == prefix + plan["suffix"]]
        if (len(matches) != 1 or matches[0].get("location") != plan["region"]
                or (matches[0].get("tags") or {}).get("project") != PROJECT):
            raise ValueError("Recovery needs the five owned services in the planned region. Stop for review.")


def refresh_region_reports(root, region):
    for module, filename in [("cloudlayer.cost_plan", "azure-cost-plan.json"),
                             ("cloudlayer.access_check", "azure-access-quota.json")]:
        path = root / "reports" / filename
        current = json.loads(path.read_text()) if path.exists() else {}
        if current.get("region") == region:
            continue
        result = subprocess.run([sys.executable, "-m", module], cwd=root,
                                capture_output=True, text=True, timeout=600)
        if result.returncode:
            raise RuntimeError(f"Could not refresh {filename}. Run its notebook and check the result.")
        updated = json.loads(path.read_text())
        if updated.get("region") != region:
            raise ValueError(f"{filename} still uses a different region.")


def preview(root, report):
    config = json.loads((root / "configs/azure.json").read_text())
    refresh_region_reports(root, config["candidate_region"])
    access = json.loads((root / "reports/azure-access-quota.json").read_text())
    cost = json.loads((root / "reports/azure-cost-plan.json").read_text())
    if (access["region"] != config["candidate_region"] or access["checks_failed"]
            or not all(v is True for v in access["control_plane_actions"].values())
            or not access["training_quota_available"]
            or (not access["container_apps_environment_slot_available"]
                and config.get("platform_template") != "infra/platform-recovery.json")):
        raise ValueError("Finish the permissions and quota checks in 14 first.")
    if not cost["within_planning_budget"] or cost["region"] != config["candidate_region"]:
        raise ValueError("Review the current region and cost plan first.")
    with tempfile.TemporaryDirectory(prefix="mlop-platform-core-") as directory:
        env = os.environ.copy()
        env["AZURE_EXTENSION_DIR"] = directory
        account = azure(["account", "show", "--query", "{id:id,state:state}"], env)
        if account["state"] != "Enabled":
            raise ValueError("The current subscription is not enabled.")
        plan = plan_for(account, config)
        def run(args):
            return azure([*args, "--subscription", account["id"]], env)
        report.update(plan)
        policies = run(["policy", "assignment", "list", "--disable-scope-strict-match",
                        "--query", "[].{parameters:parameters,enforcementMode:enforcementMode}"])
        report["allowed_regions"] = check_region_policy(policies, plan["region"])
        group = plan["resource_group"]
        exists = run(["group", "exists", "--name", group])
        if exists:
            current = run(["group", "show", "--name", group,
                           "--query", "{location:location,tags:tags}"])
            check_group(current, plan)
            report["group_reused"] = True
        else:
            remove_after = (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()
            current = run(["group", "create", "--name", group, "--location", plan["region"],
                             "--tags", f"project={PROJECT}", f"removeAfter={remove_after}",
                             "--query", "{location:location,tags:tags}"])
            report["resource_group_created"] = True
            check_group(current, plan)
        report["resource_group_location"] = current["location"]
        report["cleanup_by_utc"] = current.get("tags", {}).get("removeAfter")
        tags = {"project": PROJECT, "purpose": "course-demo"}
        if report["cleanup_by_utc"]:
            tags["removeAfter"] = report["cleanup_by_utc"]
        parameters = {"location": {"value": plan["region"]}, "suffix": {"value": plan["suffix"]},
                      "tags": {"value": tags}}
        temp = root / "tmp"
        temp.mkdir(exist_ok=True)
        parameter_path = temp / "platform-parameters.json"
        parameter_path.write_text(json.dumps({"parameters": parameters}, indent=2) + "\n")
        template = template_for(root, config)
        report["template_file"] = str(template.relative_to(root))
        if template.name == "platform-recovery.json":
            resources = run(["resource", "list", "--resource-group", group,
                             "--query", "[].{name:name,type:type,location:location,tags:tags}"])
            check_recovery_resources(resources, plan)
            report["existing_services_checked"] = True
        report["template_sha256"] = hashlib.sha256(template.read_bytes()).hexdigest()
        report["parameters_sha256"] = hashlib.sha256(parameter_path.read_bytes()).hexdigest()
        args = ["--resource-group", group, "--template-file", str(template),
                "--parameters", "@" + str(parameter_path)]
        validation = run(["deployment", "group", "validate", *args])
        if validation.get("error"):
            raise RuntimeError("ARM validation returned an error. No paid deployment was started.")
        report["validation_passed"] = True
        result = run(["deployment", "group", "what-if", *args, "--no-pretty-print",
                      "--exclude-change-types", "Ignore"])
        report["changes"] = summarize_changes(result)
        report["preview_ready"] = (result.get("status") == "Succeeded" and bool(report["changes"])
                                   and all(r["change"] in {"Create", "NoChange"} for r in report["changes"]))
        report["next"] = "Review the preview before paid deployment. Do not apply if preview_ready is false."


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "resource_group_created": False,
              "paid_resources_created": False, "validation_passed": False, "preview_ready": False, "errors": []}
    try:
        preview(root, report)
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        report["errors"].append(type(error).__name__ + ": " + str(error)
                                if not isinstance(error, subprocess.TimeoutExpired) else "Azure CLI timed out.")
    (root / "reports/azure-platform-preview.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
