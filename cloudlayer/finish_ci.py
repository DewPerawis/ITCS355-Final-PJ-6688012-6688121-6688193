import json
import os
from pathlib import Path
import re
import time
from uuid import UUID

from cloudlayer.session import ROOT, Session, command, read


REPOSITORY = "DewPerawis/MLOP-PJ"
CI_INPUTS = [".github", ".dockerignore", ".gitattributes", "Dockerfile", "dvc.yaml", "data/raw.dvc",
             "src", "service", "monitoring", "cloudlayer", "scripts", "tests", "configs",
             "requirements-local.txt", "requirements-local.lock.txt", "requirements-cloud.txt",
             "requirements-service.lock.txt", "requirements-notebook.txt", "requirements-notebook.lock.txt",
             "reports/bundle-manifest.json", "reports/golden-profiles.json", "reports/azure-blob-upload.json",
             "reports/azure-platform-deploy.json", "reports/serving-recheck/docker-image.json"]


def same_ci_source(tested, head):
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in [tested, head]):
        raise ValueError("Expected full Git commit IDs.")
    if tested == head:
        return True
    try:
        ancestor = command(["git", "merge-base", tested, head], "ci-source-ancestor").strip()
        changes = command(["git", "diff", "--name-only", tested, head, "--", *CI_INPUTS], "ci-source-diff")
    except RuntimeError:
        return False
    return ancestor == tested and not changes.strip()


def github_command(args, label):
    env = dict(os.environ, NO_COLOR="1", CLICOLOR="0", CLICOLOR_FORCE="0", GH_PROMPT_DISABLED="1")
    for key in ["GH_FORCE_TTY", "FORCE_COLOR", "GH_DEBUG", "DEBUG"]:
        env.pop(key, None)
    return command(args, label, env=env)


def github_json(args, label):
    output = github_command(args, label)
    # Terminal colors are not part of JSON.
    cleaned = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", output).strip().lstrip("\ufeff")
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{label} returned invalid JSON (length {len(output)}, position {error.pos}). "
                           "Stop and check the GitHub CLI response before retrying.") from None
    if not isinstance(value, dict):
        raise RuntimeError(label + " returned an unexpected JSON type; expected an object.")
    return value


def staging_subject(repository, settings):
    if repository.get("full_name") != REPOSITORY or settings.get("use_default") is not True:
        raise ValueError("Review the repository identity and custom OIDC template first.")
    owner, name = REPOSITORY.split("/")
    if repository["owner"]["login"] != owner:
        raise ValueError("GitHub repository owner differs from the project.")
    prefix = (f"repo:{owner}@{repository['owner']['id']}/{name}@{repository['id']}"
              if settings.get("use_immutable_subject") else "repo:" + REPOSITORY)
    if settings.get("sub_claim_prefix") != prefix:
        raise ValueError("GitHub OIDC prefix differs from the verified repository IDs.")
    return prefix + ":environment:staging"


def checked_role_id(value, name, scope, actions):
    permissions = value.get("permissions", [])
    if (value.get("roleName") != name or value.get("roleType") != "CustomRole"
            or {s.lower() for s in value.get("assignableScopes", [])} != {scope.lower()}
            or len(permissions) != 1):
        raise ValueError("The existing CI role has a different name, type, or scope.")
    permission = permissions[0]
    if (set(permission.get("actions", [])) != set(actions)
            or permission.get("notActions") or permission.get("dataActions") or permission.get("notDataActions")):
        raise ValueError("The existing CI role permissions differ from the intended limited role.")
    role_id = str(UUID(value["name"]))
    subscription = scope.split("/resourceGroups/", 1)[0]
    expected = subscription + "/providers/Microsoft.Authorization/roleDefinitions/" + role_id
    if str(value.get("id", "")).lower() != expected.lower():
        raise ValueError("The CI role ID belongs to a different subscription or definition.")
    return role_id


def assign_custom_role(cloud, principal, scope, role_id, timeout=120):
    started = time.monotonic()
    while True:
        try:
            cloud.role(principal, scope, role_id)
            return
        except RuntimeError as error:
            if "RoleDefinitionDoesNotExist" not in str(error) or time.monotonic() - started >= timeout:
                raise
            time.sleep(5)


def configure(report):
    deployed = read("reports/finish-deploy.json")
    if deployed["errors"] or not deployed.get("api_ready"):
        raise ValueError("Deploy the API first.")
    repository = github_json(["gh", "api", "repos/" + REPOSITORY], "github-repository")
    settings = github_json(["gh", "api", "repos/" + REPOSITORY + "/actions/oidc/customization/sub"], "github-oidc")
    subject = staging_subject(repository, settings)
    with Session() as cloud:
        name = "id-ci-" + cloud.plan["suffix"]
        identities = cloud.az(["identity", "list", "--resource-group", cloud.group])
        current = [value for value in identities if value["name"] == name]
        if current:
            identity = current[0]
            if (identity.get("tags") or {}).get("project") != cloud.tags["project"]:
                raise ValueError("CI identity belongs to another project.")
        else:
            identity = cloud.az(["identity", "create", "--name", name, "--resource-group", cloud.group,
                                 "--location", cloud.region, "--tags", *[f"{k}={v}" for k, v in cloud.tags.items()]])
        cloud.az(["identity", "federated-credential", "create", "--name", "github-staging", "--identity-name", name,
                  "--resource-group", cloud.group, "--issuer", "https://token.actions.githubusercontent.com",
                  "--subject", subject,
                  "--audiences", "api://AzureADTokenExchange", "--query", "{name:name}"])
        registry = cloud.get("Microsoft.ContainerRegistry/registries/" + cloud.registry, "2023-07-01")
        storage = cloud.get("Microsoft.Storage/storageAccounts/" + cloud.storage, "2023-05-01")
        cloud.role(identity["principalId"], registry["id"], "8311e382-0749-4cb8-b61a-304f252e45ec")
        cloud.role(identity["principalId"], storage["id"], "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1")
        scope = registry["id"].split("/providers/", 1)[0]
        definition = {"Name": "MLOP CI " + cloud.plan["suffix"], "IsCustom": True,
                      "Description": "Update project apps and assign their existing pull identity.",
                      "Actions": ["Microsoft.Resources/subscriptions/resourceGroups/read",
                                  "Microsoft.App/containerApps/read", "Microsoft.App/containerApps/write",
                                  "Microsoft.App/managedEnvironments/read",
                                  "Microsoft.App/managedEnvironments/join/action",
                                  "Microsoft.ManagedIdentity/userAssignedIdentities/read",
                                  "Microsoft.ManagedIdentity/userAssignedIdentities/assign/action"],
                      "NotActions": [], "DataActions": [], "NotDataActions": [], "AssignableScopes": [scope]}
        file = ROOT / "tmp/ci-role.json"
        file.write_text(json.dumps(definition))
        definitions = cloud.az(["role", "definition", "list", "--name", definition["Name"], "--scope", scope])
        if len(definitions) > 1:
            raise ValueError("More than one CI role has the project name. Review definitions before assigning.")
        value = definitions[0] if definitions else cloud.az([
            "role", "definition", "create", "--role-definition", "@" + str(file)])
        role_id = checked_role_id(value, definition["Name"], scope, definition["Actions"])
        assign_custom_role(cloud, identity["principalId"], scope, role_id)
        report["custom_role_id"] = role_id
        variables = {"AZURE_CLIENT_ID": identity["clientId"], "AZURE_TENANT_ID": cloud.account["tenantId"],
                     "AZURE_SUBSCRIPTION_ID": cloud.account["id"], "STORAGE_ACCOUNT": cloud.storage,
                     "CONTAINER_REGISTRY": cloud.host}
        (ROOT / "tmp/github-variables.json").write_text(json.dumps(variables, indent=2))
        report.update(ci_identity_configured=True, repository=REPOSITORY, oidc_subject=subject,
                      variables_file="tmp/github-variables.json", workflow_file=".github/workflows/ci.yml",
                      github_variables_configured=False,
                      next="Set repository variables, create the staging environment, and push reviewed files. Run normal and demo_failure workflows. No commit or push was performed by this script.")


def check_runs(report):
    github_command(["gh", "api", f"repos/{REPOSITORY}", "--jq", ".full_name"], "github-repository-access")
    page = github_json(["gh", "api", f"repos/{REPOSITORY}/actions/workflows?per_page=100"], "github-workflows")
    if page.get("total_count", 0) > 100:
        raise ValueError("Workflow listing needs pagination review.")
    workflows = [w for w in page["workflows"] if w["path"] == ".github/workflows/ci.yml"]
    if not workflows or workflows[0].get("state") != "active":
        report.update(ci_evidence_ready=False, pending=True, workflow_published=bool(workflows),
                      next="Complete Notebook 21 GitHub settings, commit/push reviewed files, and run normal and demo_failure workflows. Then retry ci-evidence only.")
        return
    report["workflow_published"] = True
    workflow_id = workflows[0]["id"]
    head = command(["git", "rev-parse", "HEAD"], "git-head").strip()
    dirty = command(["git", "status", "--porcelain", "--untracked-files=all", "--", *CI_INPUTS], "ci-source-status")
    if dirty.strip():
        report.update(ci_evidence_ready=False, pending=True,
                      next="Review and commit the changed CI inputs before checking runs. Saved runs do not cover uncommitted source.")
        return
    runs = github_json(["gh", "api", f"repos/{REPOSITORY}/actions/workflows/{workflow_id}/runs?per_page=30"], "github-runs")["workflow_runs"]
    good = [r for r in runs if r["conclusion"] == "success" and r.get("event") != "pull_request"]
    for success in good:
        tested = success["head_sha"]
        failed = [r for r in runs if r["head_sha"] == tested and r["conclusion"] == "failure"
                  and r.get("event") == "workflow_dispatch"]
        if not failed or not same_ci_source(tested, head):
            continue
        jobs = github_json(["gh", "api", f'repos/{REPOSITORY}/actions/runs/{success["id"]}/jobs'], "github-success-jobs")["jobs"]
        if not all(any(j["name"] == name and j["conclusion"] == "success" for j in jobs) for name in ["tests", "deploy"]):
            continue
        for failure in failed:
            jobs = github_json(["gh", "api", f'repos/{REPOSITORY}/actions/runs/{failure["id"]}/jobs'], "github-failure-jobs")["jobs"]
            if not (any(j["name"] == "tests" and j["conclusion"] == "failure" for j in jobs) and any(
                    j["name"] == "deploy" and j["conclusion"] == "skipped" for j in jobs)):
                continue
            log = github_command(["gh", "run", "view", str(failure["id"]), "--repo", REPOSITORY, "--log-failed"], "github-deliberate-failure")
            if "Deliberate CI test failure: the deployment job must be skipped." not in log:
                continue
            report.update(ci_success_run=success["html_url"], tests_blocked_deploy_runs=[failure["html_url"]],
                          tested_source_commit=tested, repository_head=head, source_matches_head=True,
                          intentional_test_failure_verified=True, ci_evidence_ready=True, pending=False,
                          next="Both runs passed the evidence checks. Documentation-only commits keep this evidence valid while CI inputs stay unchanged.")
            return
    report.update(ci_success_run=None, tests_blocked_deploy_runs=[], ci_evidence_ready=False, pending=True,
                  next="Run normal and demo_failure workflows for the reviewed source, then retry ci-evidence.")
