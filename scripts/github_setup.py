import argparse
import json
from datetime import datetime, timezone
from uuid import UUID

from cloudlayer.finish_ci import REPOSITORY, github_command, github_json
from cloudlayer.session import ROOT, read, write

KEYS = {"AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID", "STORAGE_ACCOUNT", "CONTAINER_REGISTRY"}


def check_values(values):
    if set(values) != KEYS:
        raise ValueError("Expected exactly the five CI variables; do not upload other local values.")
    for key in ["AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID"]:
        UUID(values[key])
    if not values["STORAGE_ACCOUNT"].startswith("stmloppj") or not values["CONTAINER_REGISTRY"].startswith("acrmloppj") or not values["CONTAINER_REGISTRY"].endswith(".azurecr.io"):
        raise ValueError("Use the project storage and registry from ci-setup.")


def api(path, method="GET", body=None):
    args = ["gh", "api", "repos/" + REPOSITORY + "/" + path, "--method", method]
    if body is not None:
        file = ROOT / "tmp/github-settings-request.json"
        file.write_text(json.dumps(body))
        args += ["--input", str(file)]
    return github_json(args, "github-settings")


def setup(apply=False):
    ci = read("reports/finish-ci-setup.json")
    if ci.get("errors") or not ci.get("ci_identity_configured") or ci.get("repository") != REPOSITORY:
        raise ValueError("Finish ci-setup first.")
    values = read("tmp/github-variables.json")
    check_values(values)
    github_command(["gh", "api", "repos/" + REPOSITORY, "--jq", ".full_name"], "github-repository-access")
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "repository": REPOSITORY,
              "apply": apply, "variable_names": sorted(KEYS), "github_settings_configured": False,
              "next": "Review/commit/push project files, then run normal and demo_failure workflows. No commit, push, or workflow dispatch is performed here."}
    if not apply:
        report["next"] = "Rerun with --apply to create staging and set the five repository variables. No values are printed."
        return report
    environments = api("environments?per_page=100")
    if environments.get("total_count", 0) > 100:
        raise ValueError("Environment listing needs pagination review.")
    if not any(e["name"] == "staging" for e in environments["environments"]):
        api("environments/staging", "PUT", {"deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}})
    environment = api("environments/staging")
    policy = environment.get("deployment_branch_policy") or {}
    if policy != {"protected_branches": False, "custom_branch_policies": True}:
        raise ValueError("Existing staging policy differs. Configure selected main branch in GitHub settings before retrying.")
    rules = api("environments/staging/deployment-branch-policies?per_page=100")
    if rules.get("total_count", 0) > 100:
        raise ValueError("Branch policy listing needs pagination review.")
    branches = rules["branch_policies"]
    if any(rule["name"] != "main" or rule.get("type", "branch") != "branch" for rule in branches):
        raise ValueError("Staging has other allowed branches or tags. Review settings before retrying.")
    if not branches:
        api("environments/staging/deployment-branch-policies", "POST", {"name": "main", "type": "branch"})
    for key in sorted(KEYS):
        github_command(["gh", "variable", "set", key, "--repo", REPOSITORY, "--body", values[key]], "github-variable-" + key.lower())
    confirmed = api("actions/variables?per_page=100")
    saved = {v["name"]: v["value"] for v in confirmed["variables"]}
    if any(saved.get(key) != values[key] for key in KEYS):
        raise ValueError("Repository variables did not match the prepared CI values.")
    report["github_settings_configured"] = True
    write("reports/github-settings.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Create GitHub staging settings and set the five CI variables")
    print(json.dumps(setup(parser.parse_args().apply), indent=2))
