import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from cloudlayer.platform_preview import azure, check_group, plan_for, template_for, check_recovery_resources


def check_preview(report, template, parameters):
    if (report.get("errors") or not report.get("preview_ready") or not report.get("validation_passed")
            or not report.get("changes")):
        raise ValueError("Finish and review 15 before deployment.")
    if any(row["change"] not in {"Create", "NoChange"} for row in report.get("changes", [])):
        raise ValueError("Preview includes changes that need review.")
    for key, path in [("template_sha256", template), ("parameters_sha256", parameters)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != report[key]:
            raise ValueError("Deployment files changed after preview. Rerun 15.")
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(report["checked_at"])).total_seconds()
    if age < 0 or age > 3600:
        raise ValueError("Preview is older than one hour. Rerun 15.")


def deploy(root, report):
    previous_path = root / "reports/azure-platform-deploy.json"
    if previous_path.exists():
        previous = json.loads(previous_path.read_text())
        if (previous.get("paid_resources_may_exist")
                and (any("RoleAssignmentExists" in error for error in previous.get("errors", []))
                     or previous.get("completion_mode") == "verified_existing")):
            from cloudlayer.platform_verify import verify
            verification = verify(root)
            if (verification["resource_group"] != previous["resource_group"]
                    or verification["region"] != previous["region"]):
                raise ValueError("Current subscription or region differs from the failed deployment.")
            (root / "reports/azure-platform-verification.json").write_text(json.dumps(verification, indent=2) + "\n")
            report["paid_resources_may_exist"] = True
            if not verification["platform_verified"]:
                raise ValueError("Existing platform checks failed: " + ", ".join(verification["checks_failed"]))
            report.update(verification)
            report["platform_created"] = True
            report["completion_mode"] = "verified_existing"
            report["deployment_retried"] = False
            report["next"] = "Existing services and workspace roles are verified. Test data access and connect the pipeline next."
            return
    preview = json.loads((root / "reports/azure-platform-preview.json").read_text())
    config = json.loads((root / "configs/azure.json").read_text())
    template, parameters = template_for(root, config), root / "tmp/platform-parameters.json"
    check_preview(preview, template, parameters)
    with tempfile.TemporaryDirectory(prefix="mlop-platform-deploy-") as directory:
        env = os.environ.copy()
        env["AZURE_EXTENSION_DIR"] = directory
        account = azure(["account", "show", "--query", "{id:id,state:state}"], env)
        plan = plan_for(account, config)
        if account["state"] != "Enabled" or plan["resource_group"] != preview["resource_group"]:
            raise ValueError("Current subscription differs from the preview. Rerun 15.")
        if plan["region"] != preview["region"]:
            raise ValueError("Region differs from the preview. Rerun 15.")
        report.update(plan)
        report["cleanup_by_utc"] = preview.get("cleanup_by_utc")
        if not report["cleanup_by_utc"] or datetime.fromisoformat(report["cleanup_by_utc"]) <= datetime.now(timezone.utc):
            raise ValueError("The planned cleanup time has passed. Review the plan before deployment.")
        def run(args):
            return azure([*args, "--subscription", account["id"]], env)
        group = run(["group", "show", "--name", plan["resource_group"],
                     "--query", "{location:location,tags:tags}"])
        check_group(group, plan)
        if template.name == "platform-recovery.json":
            resources = run(["resource", "list", "--resource-group", plan["resource_group"],
                             "--query", "[].{name:name,type:type,location:location,tags:tags}"])
            check_recovery_resources(resources, plan)
        report["template_file"] = str(template.relative_to(root))
        report["apply_started"] = True
        report["paid_resources_may_exist"] = True
        result = run(["deployment", "group", "create", "--name", "mlop-platform",
                      "--resource-group", plan["resource_group"], "--mode", "Incremental",
                      "--template-file", str(template), "--parameters", "@" + str(parameters),
                      "--query", "{state:properties.provisioningState}"])
        report["deployment_state"] = result.get("state")
        report["resources"] = run(["resource", "list", "--resource-group", plan["resource_group"],
                                   "--query", "[].{name:name,type:type,location:location}"])
        report["platform_created"] = report["deployment_state"] == "Succeeded"
        report["next"] = "Check created services and data/identity access, then upload the image and connect the pipeline."


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "apply_started": False,
              "paid_resources_may_exist": False, "platform_created": False, "errors": []}
    try:
        deploy(root, report)
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        report["errors"].append(type(error).__name__ + ": " + str(error)
                                if not isinstance(error, subprocess.TimeoutExpired) else "Azure CLI timed out.")
        if report["apply_started"]:
            report["next"] = "Deployment may be partial or still running. Check the project group before retrying; do not assume zero cost."
    (root / "reports/azure-platform-deploy.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
