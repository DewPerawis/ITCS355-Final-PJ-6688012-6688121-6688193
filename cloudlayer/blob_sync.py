import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, NAMESPACE_URL, uuid5

from cloudlayer.platform_preview import PROJECT, azure, check_group, plan_for
from cloudlayer.platform_verify import has_role, same_region


BLOB_ROLE = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files_for(root):
    source = json.loads((root / "reports/data-source.json").read_text())
    bundle = json.loads((root / "reports/bundle-manifest.json").read_text())
    prepared = json.loads((root / "reports/prepared-data.json").read_text())
    pinned = {source["raw_file"]: source["sha256"], bundle["artifact"]: bundle["artifact_sha256"],
              "data/processed/profiles.csv": prepared["files"]["data/processed/profiles.csv"],
              "configs/data.json": prepared["files"]["configs/data.json"]}
    if source["sha256"] != bundle["raw_sha256"] or source["sha256"] != prepared["raw_sha256"]:
        raise ValueError("Data and bundle lineage do not match.")
    rows = []
    for name in [*pinned, "reports/data-source.json", "reports/bundle-manifest.json", "data/raw.dvc"]:
        path = root / name
        if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError("Missing file or path outside the project.")
        sha = digest(path)
        if name in pinned and sha != pinned[name]:
            raise ValueError("File changed after its saved check: " + name)
        rows.append({"file": name, "bytes": path.stat().st_size, "sha256": sha,
                     "blob": f"snapshots/{sha}/{path.name}"})
    return rows


def connect(root, env):
    verified = json.loads((root / "reports/azure-platform-verification.json").read_text())
    if not verified.get("platform_verified") or verified.get("checks_failed"):
        raise ValueError("Finish platform verification in 16 first.")
    config = json.loads((root / "configs/azure.json").read_text())
    account = azure(["account", "show", "--query", "{id:id,state:state,userType:user.type}"], env)
    plan = plan_for(account, config)
    if (account["state"] != "Enabled" or account["userType"] != "user"
            or plan["resource_group"] != verified["resource_group"] or plan["region"] != verified["region"]):
        raise ValueError("Use the same enabled user subscription as 16.")
    def run(args):
        return azure([*args, "--subscription", account["id"]], env)
    group = run(["group", "show", "--name", plan["resource_group"], "--query", "{location:location,tags:tags}"])
    check_group(group, plan)
    name = "stmloppj" + plan["suffix"]
    scope = f'/subscriptions/{account["id"]}/resourceGroups/{plan["resource_group"]}/providers/Microsoft.Storage/storageAccounts/{name}'
    storage = run(["rest", "--method", "get", "--url", f"https://management.azure.com{scope}?api-version=2023-05-01"])
    if (not same_region(storage["location"], plan["region"]) or storage["tags"].get("project") != PROJECT
            or storage["properties"].get("allowSharedKeyAccess") is not False):
        raise ValueError("Storage ownership, region, or identity settings differ.")
    container = run(["rest", "--method", "get", "--url",
                     f"https://management.azure.com{scope}/blobServices/default/containers/mlop-data?api-version=2023-05-01"])
    if container["properties"].get("publicAccess") != "None":
        raise ValueError("The project data container is not private.")
    common = ["--account-name", name, "--container-name", "mlop-data", "--auth-mode", "login"]
    return run, plan, scope, common


def access(root, report, env):
    run, plan, scope, common = connect(root, env)
    report.update(plan)
    principal = str(UUID(azure(["ad", "signed-in-user", "show", "--query", "id"], env)))
    url = f"https://management.azure.com{scope}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&$filter=atScope()"
    def assigned():
        page = run(["rest", "--method", "get", "--url", url])
        if page.get("nextLink"):
            raise ValueError("Role results need pagination review.")
        return has_role(page["value"], principal, scope, BLOB_ROLE)
    report["user_role_created"] = False
    if not assigned():
        name = str(uuid5(NAMESPACE_URL, scope.lower() + principal + BLOB_ROLE))
        try:
            run(["role", "assignment", "create", "--name", name, "--assignee-object-id", principal,
                 "--assignee-principal-type", "User", "--role", BLOB_ROLE, "--scope", scope,
                 "--query", "{roleDefinitionId:roleDefinitionId}"])
            report["user_role_created"] = True
        except RuntimeError as error:
            if "RoleAssignmentExists" not in str(error) or not assigned():
                raise
    report["role_scope"] = "project storage account"
    for attempt in range(6):
        try:
            run(["storage", "blob", "list", *common, "--num-results", "1", "--query", "[].name"])
            report["blob_access_ready"] = True
            return
        except RuntimeError:
            if attempt == 5:
                raise RuntimeError("Blob access is not ready. The role may still be propagating; rerun this access cell in a few minutes.")
            time.sleep(10)


def upload(root, report, env):
    previous = json.loads((root / "reports/azure-blob-access.json").read_text())
    if previous.get("errors") or not previous.get("blob_access_ready"):
        raise ValueError("Run the Blob access cell first.")
    rows = files_for(root)
    run, plan, scope, common = connect(root, env)
    report.update(plan)
    if plan["resource_group"] != previous["resource_group"] or plan["region"] != previous["region"]:
        raise ValueError("Blob access was checked for a different project or region.")
    report["files"] = []
    for row in rows:
        path = root / row["file"]
        if digest(path) != row["sha256"]:
            raise ValueError("Local file changed during upload.")
        exists = run(["storage", "blob", "exists", *common, "--name", row["blob"]])["exists"]
        if not exists:
            run(["storage", "blob", "upload", *common, "--name", row["blob"], "--file", str(path),
                 "--overwrite", "false", "--validate-content", "--metadata", "sha256=" + row["sha256"],
                 "--query", "{etag:etag}"])
        with tempfile.TemporaryDirectory(prefix="mlop-blob-check-") as directory:
            downloaded = Path(directory) / path.name
            run(["storage", "blob", "download", *common, "--name", row["blob"], "--file", str(downloaded),
                 "--overwrite", "false", "--query", "{name:name}"])
            matches = digest(downloaded) == row["sha256"]
        report["files"].append({**row, "uploaded_now": not exists, "download_sha256_matches": matches})
        if not matches:
            raise ValueError("Downloaded Blob content differs: " + row["blob"])
    report["all_hashes_match"] = len(report["files"]) == len(rows)
    report["data_uploaded"] = report["all_hashes_match"]
    report["next"] = "Configure the DVC Azure remote, then connect Azure ML training and registry."
    report["limits"] = ["These are verified Blob snapshots, not a DVC remote push or an Azure ML training run."]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["access", "upload"])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "phase": args.phase,
              "errors": [], "blob_access_ready": False} if args.phase == "access" else {
                  "checked_at": datetime.now(timezone.utc).isoformat(), "phase": args.phase,
                  "errors": [], "data_uploaded": False, "all_hashes_match": False}
    try:
        with tempfile.TemporaryDirectory(prefix="mlop-blob-cli-") as directory:
            env = dict(os.environ, AZURE_EXTENSION_DIR=directory)
            (access if args.phase == "access" else upload)(root, report, env)
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        report["errors"].append("Azure command timed out." if isinstance(error, subprocess.TimeoutExpired)
                                else type(error).__name__ + ": " + str(error))
    output = "azure-blob-access.json" if args.phase == "access" else "azure-blob-upload.json"
    (root / "reports" / output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
