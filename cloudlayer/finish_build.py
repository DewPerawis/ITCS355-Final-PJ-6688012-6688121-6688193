import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from cloudlayer.blob_sync import digest
from cloudlayer.session import ROOT, Session, command, read


def source_hash():
    paths = [*sorted((ROOT / "src").glob("*.py")), *sorted((ROOT / "service").glob("*.py")),
             ROOT / "Dockerfile", ROOT / "requirements-service.lock.txt", ROOT / "scripts/train_selected.py"]
    content = "\n".join(str(p.relative_to(ROOT)) + ":" + digest(p) for p in paths)
    return hashlib.sha256(content.encode()).hexdigest()


def assets(report):
    uploaded = read("reports/azure-blob-upload.json")
    if uploaded["errors"] or not uploaded["all_hashes_match"]:
        raise ValueError("Finish 17 first.")
    manifest = read("reports/bundle-manifest.json")
    if digest(ROOT / manifest["artifact"]) != manifest["artifact_sha256"]:
        raise ValueError("Canonical model changed.")
    command([sys.executable, "-m", "unittest", "discover", "-s", "tests"], "finish-tests")
    report["local_tests_passed"] = True
    with Session() as cloud:
        remote = "azure://mlop-data/dvc"
        command([sys.executable, "-m", "dvc", "remote", "add", "--local", "--force", "azure", remote], "dvc-remote")
        command([sys.executable, "-m", "dvc", "remote", "modify", "--local", "azure", "account_name", cloud.storage], "dvc-account")
        command([sys.executable, "-m", "dvc", "push", "data/raw.dvc", "-r", "azure"], "dvc-push", env=cloud.env)
        with tempfile.TemporaryDirectory(prefix="mlop-dvc-fresh-") as directory:
            fresh = Path(directory)
            (fresh / "data").mkdir()
            shutil.copy2(ROOT / "data/raw.dvc", fresh / "data/raw.dvc")
            command([sys.executable, "-m", "dvc", "init", "--no-scm"], "dvc-fresh-init", cwd=fresh)
            command([sys.executable, "-m", "dvc", "remote", "add", "azure", remote], "dvc-fresh-remote", cwd=fresh)
            command([sys.executable, "-m", "dvc", "remote", "modify", "azure", "account_name", cloud.storage], "dvc-fresh-account", cwd=fresh)
            command([sys.executable, "-m", "dvc", "pull", "data/raw.dvc", "-r", "azure"], "dvc-fresh-pull", cwd=fresh, env=cloud.env)
            if digest(fresh / "data/raw/google_review_ratings.csv") != manifest["raw_sha256"]:
                raise ValueError("Fresh DVC pull differs from pinned data.")
        report["dvc_fresh_pull_passed"] = True
        tag = "finish-" + manifest["model_version"] + "-" + source_hash()[:12]
        local = "mlop-pj-api:" + tag
        base = read("reports/serving-recheck/docker-image.json")["base_image"]
        command(["docker", "build", "--build-arg", "PYTHON_IMAGE=" + base,
                 "--build-arg", "MODEL_VERSION=" + manifest["model_version"], "-t", local, "."], "finish-build", timeout=1200)
        command(["az", "acr", "login", "--name", cloud.registry, "--subscription", cloud.account["id"],
                 "--only-show-errors"], "registry-login", env=cloud.env)
        image = cloud.host + "/travel-style:" + tag
        command(["docker", "tag", local, image], "finish-tag")
        command(["docker", "push", image], "finish-push", timeout=1200)
        digest_value = cloud.az(["acr", "repository", "show", "--name", cloud.registry,
                                 "--image", "travel-style:" + tag, "--query", "digest"])
        if not isinstance(digest_value, str) or not digest_value.startswith("sha256:"):
            raise ValueError("Registry did not return an immutable digest.")
        report.update(model_version=manifest["model_version"], artifact_sha256=manifest["artifact_sha256"],
                      source_sha256=source_hash(), local_image=local,
                      image_uri=cloud.host + "/travel-style@" + digest_value, assets_ready=True)
        workspace = cloud.get("Microsoft.MachineLearningServices/workspaces/" + cloud.workspace, "2026-03-01")
        values = {"CLOUD_PROVIDER": "azure", "PROJECT_ID": cloud.tags["project"], "REGION": cloud.region,
                  "BLOB_URI": "https://" + cloud.storage + ".blob.core.windows.net/mlop-data",
                  "CONTAINER_REGISTRY": cloud.host,
                  "MLFLOW_TRACKING_URI": workspace["properties"].get("mlflowTrackingUri", "sqlite:///mlflow.db"),
                  "TRAINING_TARGET": workspace["id"] + "/computes/cpu-small", "MODEL_REGISTRY_NAME": "travel-style",
                  "ENDPOINT_NAME": cloud.app, "ENDPOINT_URL": "", "METRICS_NAMESPACE": "itcs355",
                  "SECRET_STORE_PATH": "https://kv-mlop-pj-" + cloud.plan["suffix"] + ".vault.azure.net/",
                  "IDENTITY_REF": "", "BUDGET_LIMIT_THB": "150"}
        (ROOT / "cloud.env").write_text("\n".join(key + "=" + str(value) for key, value in values.items()) + "\n")


def training_submit(report):
    built = read("reports/finish-assets.json")
    if not built.get("assets_ready") or built["errors"]:
        raise ValueError("Finish the assets cell first.")
    previous = ROOT / "reports/finish-training-submit.json"
    if previous.exists():
        saved = read("reports/finish-training-submit.json")
        if saved.get("job_name") and saved.get("image_uri") == built["image_uri"]:
            with Session() as cloud:
                jobs = cloud.ml(["job", "list", "--query", "[?name=='" + saved["job_name"] + "'].name"])
                if jobs:
                    report.update(job_name=saved["job_name"], image_uri=built["image_uri"], submitted=True, reused_job=True)
                    return
    code = ROOT / "tmp/aml-training-code"
    code.mkdir(parents=True, exist_ok=True)
    for name in ["bundle-manifest.json", "prepared-data.json", "selection.json", "golden-profiles.json"]:
        shutil.copy2(ROOT / "reports" / name, code / name)
    shutil.copy2(ROOT / read("reports/bundle-manifest.json")["artifact"], code / "bundle.joblib")
    shutil.copy2(ROOT / "scripts/train_selected.py", code / "train_selected.py")
    from datetime import datetime, timezone
    with Session() as cloud:
        compute_file = ROOT / "tmp/aml-compute.json"
        compute_file.write_text(json.dumps({"$schema": "https://azuremlschemas.azureedge.net/latest/amlCompute.schema.json",
            "name": "cpu-small", "type": "amlcompute", "size": "Standard_DS2_v2", "tier": "dedicated",
            "min_instances": 0, "max_instances": 1, "idle_time_before_scale_down": 120,
            "ssh_public_access_enabled": False, "identity": {"type": "system_assigned"}, "tags": cloud.tags}))
        current = cloud.ml(["compute", "list", "--query", "[?name=='cpu-small']"])
        if not current:
            compute = cloud.ml(["compute", "create", "--file", str(compute_file)])
        else:
            compute = cloud.ml(["compute", "show", "--name", "cpu-small"])
            if (compute.get("size") != "Standard_DS2_v2" or compute.get("max_instances") != 1
                    or compute.get("min_instances") != 0):
                raise ValueError("Existing training compute differs. Stop for review.")
        principal = (compute.get("identity") or {}).get("principal_id")
        if not principal:
            raise ValueError("Training compute has no system identity.")
        storage_scope = cloud.get("Microsoft.Storage/storageAccounts/" + cloud.storage, "2023-05-01")["id"]
        cloud.role(principal, storage_scope, "ba92f5b4-2d11-453d-a403-e96b0029c9fe")
        registry = cloud.get("Microsoft.ContainerRegistry/registries/" + cloud.registry, "2023-07-01")
        cloud.role(principal, registry["id"], "7f951dda-4ed3-4680-a7ca-43fe172d538d")
        datastore = {"$schema": "https://azuremlschemas.azureedge.net/latest/azureBlob.schema.json",
                     "name": "projectdata", "type": "azure_blob", "account_name": cloud.storage,
                     "container_name": "mlop-data", "protocol": "https", "tags": cloud.tags}
        file = ROOT / "tmp/aml-datastore.json"
        file.write_text(json.dumps(datastore))
        cloud.ml(["datastore", "create", "--file", str(file), "--query", "{name:name}"])
        input_row = next(r for r in read("reports/azure-blob-upload.json")["files"] if r["file"] == "data/processed/profiles.csv")
        job_name = "train-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        job = {"$schema": "https://azuremlschemas.azureedge.net/latest/commandJob.schema.json", "type": "command",
               "name": job_name, "experiment_name": "travel-style", "code": str(code),
               "command": "python train_selected.py --profiles ${{inputs.profiles}} --output ${{outputs.model}}",
               "compute": "azureml:cpu-small", "identity": {"type": "managed"},
               "environment": {"image": built["image_uri"]},
               "inputs": {"profiles": {"type": "uri_file", "mode": "download",
                                      "path": "azureml://datastores/projectdata/paths/" + input_row["blob"]}},
               "outputs": {"model": {"type": "uri_folder", "mode": "upload"}},
               "resources": {"instance_count": 1}, "limits": {"timeout": 900},
               "environment_variables": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"},
               "tags": {**cloud.tags, "raw_sha256": read("reports/bundle-manifest.json")["raw_sha256"],
                        "artifact_sha256": built["artifact_sha256"], "source_sha256": built["source_sha256"]}}
        file = ROOT / "tmp/aml-job.json"
        file.write_text(json.dumps(job))
        report.update(job_name=job_name, image_uri=built["image_uri"], submitted=False)
        # Preserve the job name before a timeout so reruns can inspect the same submission.
        from cloudlayer.session import write
        write("reports/finish-training-submit.json", report)
        result = cloud.ml(["job", "create", "--file", str(file), "--query", "{name:name,status:status}"])
        report.update(job_name=result["name"], status=result["status"], submitted=True)


def registry_version(values, job_name, artifact_sha256, source_sha256):
    used = []
    matches = []
    for value in values:
        version = str(value["name"]).rsplit("/", 1)[-1]
        if not version.isdigit() or not 1 <= int(version) < 2147483647:
            raise ValueError("Existing model version is outside the supported numeric selection range.")
        used.append(int(version))
        tags = value.get("properties", {}).get("tags", {})
        if tags.get("training_job") == job_name:
            if tags.get("canonical_sha256") != artifact_sha256 or tags.get("source_sha256") != source_sha256:
                raise ValueError("The same training job has conflicting registry lineage.")
            if value.get("properties", {}).get("provisioningState") not in {None, "Succeeded"}:
                raise ValueError("An existing model registration is not ready; inspect it before retrying.")
            matches.append(version)
    if matches:
        return min(matches, key=int), True
    version = max(used, default=0) + 1
    if version >= 2147483647:
        raise ValueError("No next model version is available in the supported numeric range.")
    return str(version), False


def training_finish(report):
    submitted = read("reports/finish-training-submit.json")
    with Session() as cloud:
        state = cloud.ml(["job", "show", "--name", submitted["job_name"], "--query", "{status:status}"])["status"]
        report.update(job_name=submitted["job_name"], status=state, registry_ready=False)
        if state not in {"Completed", "Failed", "Canceled", "NotResponding"}:
            report["pending"] = True
            report["next"] = "Training is still running. Continue independent cells, then rerun this cell."
            return
        if state != "Completed":
            raise RuntimeError("Azure ML training stopped with status " + state + ". Inspect job logs before resubmitting.")
        folder = ROOT / "tmp/aml-training-output"
        cloud.ml(["job", "download", "--name", submitted["job_name"], "--output-name", "model", "--download-path", str(folder)])
        proofs = list(folder.rglob("training-proof.json"))
        if len(proofs) != 1:
            raise ValueError("Expected one training proof.")
        proof = json.loads(proofs[0].read_text())
        if (not proof.get("fresh_fit_equivalent")
                or proof["canonical_sha256"] != read("reports/bundle-manifest.json")["artifact_sha256"]
                or digest(proofs[0].parent / "bundle.joblib") != proof["canonical_sha256"]):
            raise ValueError("Cloud training did not reproduce the tested bundle.")
        from cloudlayer.session import write
        write("reports/azure-training-proof.json", proof)
        source_sha256 = read("reports/finish-assets.json")["source_sha256"]
        try:
            page = cloud.get("Microsoft.MachineLearningServices/workspaces/" + cloud.workspace +
                             "/models/travel-style/versions", "2026-03-01")
        except RuntimeError as error:
            if "ModelNotFound" not in str(error):
                raise
            page = {"value": []}
        if page.get("nextLink"):
            raise ValueError("Model versions need pagination review before choosing a new version.")
        model_version, reused = registry_version(page["value"], submitted["job_name"],
                                                 proof["canonical_sha256"], source_sha256)
        if reused:
            report.update(registered_name="travel-style", registered_version=model_version,
                          fresh_fit_equivalent=True, registry_ready=True, registration_reused=True)
            return
        config = {"$schema": "https://azuremlschemas.azureedge.net/latest/model.schema.json",
                  "name": "travel-style", "version": model_version, "type": "custom_model",
                  "path": f'azureml://jobs/{submitted["job_name"]}/outputs/model/paths/',
                  "tags": {"training_job": submitted["job_name"], "canonical_sha256": proof["canonical_sha256"],
                           "source_sha256": source_sha256}}
        file = ROOT / "tmp/aml-model.json"
        file.write_text(json.dumps(config))
        value = cloud.ml(["model", "create", "--file", str(file), "--query", "{name:name,version:version}"])
        report.update(registered_name=value["name"], registered_version=value["version"],
                      fresh_fit_equivalent=True, registry_ready=True, registration_reused=False)
