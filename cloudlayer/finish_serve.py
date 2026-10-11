import time
from datetime import datetime, timezone

from cloudlayer.session import ROOT, Session, read, write
from scripts.http_check import http_call, load_check, smoke


def app_body(cloud, image, identity, stage="production", fault=""):
    return {"location": cloud.region, "tags": cloud.tags,
            "identity": {"type": "UserAssigned", "userAssignedIdentities": {identity: {}}},
            "properties": {"managedEnvironmentId": cloud.base.replace("https://management.azure.com", "") +
                           "Microsoft.App/managedEnvironments/" + cloud.environment,
                "configuration": {"activeRevisionsMode": "Single",
                    "ingress": {"external": True, "targetPort": 8000, "transport": "auto", "allowInsecure": False},
                    "registries": [{"server": cloud.host, "identity": identity}]},
                "template": {
                    "containers": [{"name": "api", "image": image, "resources": {"cpu": 1, "memory": "2Gi"},
                        "env": [{"name": "DEPLOYMENT_STAGE", "value": stage},
                                {"name": "MLOP_FAILURE_MODE", "value": fault}],
                        "probes": [{"type": "Readiness", "httpGet": {"path": "/ready", "port": 8000},
                                    "initialDelaySeconds": 5, "periodSeconds": 5, "failureThreshold": 12}]}],
                    "scale": {"minReplicas": 0, "maxReplicas": 1, "cooldownPeriod": 30,
                              "rules": [{"name": "http", "http": {"metadata": {"concurrentRequests": "10"}}}]}}}}


def identity_for(cloud):
    name = "id-api-" + cloud.plan["suffix"]
    identities = cloud.az(["identity", "list", "--resource-group", cloud.group])
    matches = [r for r in identities if r["name"] == name]
    if matches:
        identity = matches[0]
        if (identity.get("tags") or {}).get("project") != cloud.tags["project"]:
            raise ValueError("API identity has a different owner.")
    else:
        identity = cloud.az(["identity", "create", "--name", name, "--resource-group", cloud.group,
                             "--location", cloud.region, "--tags", *[f"{k}={v}" for k, v in cloud.tags.items()]])
    registry = cloud.get("Microsoft.ContainerRegistry/registries/" + cloud.registry, "2023-07-01")
    cloud.role(identity["principalId"], registry["id"], "7f951dda-4ed3-4680-a7ca-43fe172d538d")
    return identity["id"]


def wait_ready(cloud, name, timeout=300):
    started = time.perf_counter()
    while time.perf_counter() - started < timeout:
        value = cloud.get("Microsoft.App/containerApps/" + name, "2025-07-01")
        state = value["properties"].get("provisioningState")
        if state in {"Failed", "Canceled"}:
            raise RuntimeError("Container App provisioning failed. Inspect its system logs before retrying.")
        host = (value["properties"].get("configuration", {}).get("ingress") or {}).get("fqdn")
        if host:
            try:
                status, _, elapsed = http_call("https://" + host, "/ready")
                if status == 200:
                    return "https://" + host, time.perf_counter() - started, elapsed
            except (OSError, ValueError):
                pass
        time.sleep(5)
    raise RuntimeError("App did not become ready within five minutes. Check image pull and system logs; do not assume failure means zero cost.")



def wait_canary(cloud, name, expected, model_version, timeout=180):
    started = time.monotonic()
    consecutive = 0
    last_status = None
    while time.monotonic() - started < timeout:
        value = cloud.get("Microsoft.App/containerApps/" + name, "2025-07-01")
        properties = value["properties"]
        if properties.get("provisioningState") in {"Failed", "Canceled"}:
            raise RuntimeError("Staging update failed. Inspect system logs.")
        host = (properties.get("configuration", {}).get("ingress") or {}).get("fqdn")
        if host and properties.get("provisioningState") == "Succeeded":
            url = "https://" + host
            try:
                ready_code, ready_body, _ = http_call(url, "/ready")
                last_status, body, _ = http_call(url, "/canary")
                semantic_match = (body.get("passed") is True and body.get("model_version") == model_version
                                  if expected == 200 else body.get("detail") == "Semantic canary failed.")
                good = (ready_code == 200 and ready_body.get("model_version") == model_version
                        and last_status == expected and semantic_match)
                consecutive = consecutive + 1 if good else 0
                if consecutive >= 2:
                    return url, last_status
            except (OSError, ValueError):
                consecutive = 0
        else:
            consecutive = 0
        time.sleep(5)
    raise RuntimeError(f"Staging canary did not reach {expected} twice within {timeout}s; last status: {last_status}.")


def wait_staging_config(cloud, name, fault, timeout=180):
    started = time.monotonic()
    while time.monotonic() - started < timeout:
        app = cloud.get("Microsoft.App/containerApps/" + name, "2025-07-01")
        properties = app["properties"]
        if properties.get("provisioningState") in {"Failed", "Canceled"}:
            raise RuntimeError("Staging configuration update failed.")
        containers = properties.get("template", {}).get("containers", [])
        env = {row["name"]: row.get("value") for row in containers[0].get("env", [])} if containers else {}
        if properties.get("provisioningState") == "Succeeded" and env.get("MLOP_FAILURE_MODE") == fault:
            return
        time.sleep(5)
    raise RuntimeError("Staging settings did not finish updating. Inspect the app before retrying.")


def restart_staging(cloud, name, timeout=180):
    if name != "failure-" + cloud.plan["suffix"]:
        raise ValueError("Stop/start is restricted to the failure demo app.")
    app = cloud.get("Microsoft.App/containerApps/" + name, "2025-07-01")
    if (app.get("tags") or {}).get("project") != cloud.tags["project"]:
        raise ValueError("The staging app belongs to another project.")
    url = cloud.base + "Microsoft.App/containerApps/" + name
    try:
        cloud.az(["rest", "--method", "post", "--url", url + "/stop?api-version=2025-07-01"])
        started = time.monotonic()
        while time.monotonic() - started < timeout:
            app = cloud.get("Microsoft.App/containerApps/" + name, "2025-07-01")
            if app["properties"].get("runningStatus") == "Stopped":
                break
            time.sleep(5)
        else:
            raise RuntimeError("Staging did not stop in time. Start was still requested in finally.")
    finally:
        cloud.az(["rest", "--method", "post", "--url", url + "/start?api-version=2025-07-01"])


def restore_staging(cloud, name, assets, report):
    report["recovery_started_at"] = datetime.now(timezone.utc).isoformat()
    identity = identity_for(cloud)
    cloud.put("Microsoft.App/containerApps/" + name, "2025-07-01",
              app_body(cloud, assets["image_uri"], identity, "staging", "off"))
    wait_staging_config(cloud, name, "off")
    restart_staging(cloud, name)
    url, code = wait_canary(cloud, name, 200, assets["model_version"])
    report.update(recovered_at=datetime.now(timezone.utc).isoformat(), recovery_canary_status=code,
                  recovered=True, recovery_url=url, recovery_method="Restore configuration, stop/start staging, and confirm semantic canary twice")


def recovery(report):
    previous = read("reports/finish-failure.json")
    if not previous.get("failure_detected") or previous.get("observed_canary_status") != 503:
        raise ValueError("No saved semantic failure evidence. Run the failure demo first.")
    assets = read("reports/finish-assets.json")
    with Session() as cloud:
        name = "failure-" + cloud.plan["suffix"]
        if previous.get("failure_app") != name:
            raise ValueError("Saved failure belongs to a different app.")
        restore_staging(cloud, name, assets, report)
    repaired = dict(previous)
    repaired["previous_errors"] = previous.get("errors", [])
    repaired["errors"] = []
    repaired.update({key: value for key, value in report.items() if key.startswith("recover")})
    repaired["failure_demo_passed"] = True
    repaired["recovery_checked_at"] = report["checked_at"]
    repaired["next"] = "Check the actual alert record. The original failure and error were preserved in history."
    write("reports/finish-failure.json", repaired)
    report.update(failure_app=name, failure_demo_passed=True, original_detected_at=previous.get("detected_at"))


def deploy(report):
    assets = read("reports/finish-assets.json")
    if assets["errors"] or not assets.get("assets_ready"):
        raise ValueError("Finish the assets cell first.")
    with Session() as cloud:
        identity = identity_for(cloud)
        body = app_body(cloud, assets["image_uri"], identity)
        report["cloud_writes_started"] = True
        cloud.put("Microsoft.App/containerApps/" + cloud.app, "2025-07-01", body)
        url, ready_seconds, first_ms = wait_ready(cloud, cloud.app)
        report.update(url=url, image_uri=assets["image_uri"], app_name=cloud.app,
                      deployment_to_ready_seconds=ready_seconds, first_ready_request_ms=first_ms,
                      first_request_scope="First successful readiness request after deployment; not an isolated scale-from-zero benchmark.")
        file = ROOT / "cloud.env"
        if file.exists():
            lines = file.read_text().splitlines()
            lines = ["ENDPOINT_URL=" + url if line.startswith("ENDPOINT_URL=") else
                     "IDENTITY_REF=" + identity if line.startswith("IDENTITY_REF=") else line for line in lines]
            file.write_text("\n".join(lines) + "\n")
        fixture = read("reports/golden-profiles.json")
        checked = smoke(url, fixture)
        canary_code, _, _ = http_call(url, "/canary")
        if canary_code != 200:
            raise ValueError("Deployed semantic canary failed.")
        write("reports/azure-smoke.json", checked)
        load = load_check(url, fixture)
        load["scope"] = "Azure HTTPS endpoint measured from the user's WSL machine"
        write("reports/azure-load.json", load)
        if load["errors"]:
            raise ValueError("Azure load check has errors.")
        report.update(api_ready=True, smoke_passed=True, canary_passed=True,
                      p95_ms=load["p95_ms"], latency_target_met=load["target_met"],
                      limits=["Client latency includes internet routing; the 300 ms target remains open if latency_target_met is false.",
                              "The staging demo endpoint is public. Do not submit private profiles."])


def failure(report):
    monitor = read("reports/finish-monitor.json")
    if monitor["errors"] or not monitor.get("monitor_ready"):
        raise ValueError("Configure the dashboard and alert before the failure demo.")
    assets = read("reports/finish-assets.json")
    with Session() as cloud:
        identity = identity_for(cloud)
        name = "failure-" + cloud.plan["suffix"]
        report.update(failure_app=name, failure_started_at=datetime.now(timezone.utc).isoformat())
        try:
            cloud.put("Microsoft.App/containerApps/" + name, "2025-07-01",
                      app_body(cloud, assets["image_uri"], identity, "staging", "wrong_mapping"))
            wait_staging_config(cloud, name, "wrong_mapping")
            restart_staging(cloud, name)
            url, code = wait_canary(cloud, name, 503, assets["model_version"])
            report.update(detected_at=datetime.now(timezone.utc).isoformat(), observed_canary_status=code)
            if code != 503:
                raise ValueError("The controlled mapping failure was not detected.")
            report["failure_detected"] = True
        finally:
            # A ready model can still have a wrong mapping; check semantic recovery.
            restore_staging(cloud, name, assets, report)
        if not report.get("recovered"):
            raise ValueError("Staging recovery check failed.")
        report["failure_demo_passed"] = report.get("failure_detected", False) and report["recovered"]
        report["next"] = "Refresh telemetry and check that the alert fired. Both apps scale to zero when idle."


def cold(report):
    deployed = read("reports/finish-deploy.json")
    with Session() as cloud:
        started = time.perf_counter()
        while time.perf_counter() - started < 180:
            app = cloud.get("Microsoft.App/containerApps/" + cloud.app, "2025-07-01")
            revision = app["properties"].get("latestReadyRevisionName")
            if not revision:
                raise ValueError("No ready revision exists.")
            replicas = cloud.get("Microsoft.App/containerApps/" + cloud.app + "/revisions/" + revision + "/replicas", "2025-07-01")
            if not replicas.get("value"):
                report["zero_replicas_observed_at"] = datetime.now(timezone.utc).isoformat()
                status, _, elapsed = http_call(deployed["url"], "/ready", timeout=120)
                if status != 200:
                    raise ValueError("First request after zero replicas did not become ready.")
                report.update(cold_start_measured=True, first_request_ms=elapsed,
                              scope="WSL HTTPS readiness request after ARM reported zero replicas; includes network and scale activation.")
                return
            time.sleep(5)
        report.update(cold_start_measured=False, pending=True,
                      next="The app still has a replica. Stop browser/API traffic and rerun this cell later.")
