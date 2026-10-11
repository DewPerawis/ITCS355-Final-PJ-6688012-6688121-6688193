import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cloudlayer.session import Session, read


def collect():
    def flag(file, key):
        path = ROOT / "reports" / file
        if not path.exists():
            return False
        report = json.loads(path.read_text())
        return not report.get("errors") and report.get(key) is True
    env = ROOT / "cloud.env"
    values = dict(line.split("=", 1) for line in env.read_text().splitlines() if "=" in line and not line.startswith("#")) if env.exists() else {}
    with Session() as cloud:
        vault = cloud.get("Microsoft.KeyVault/vaults/kv-mlop-pj-" + cloud.plan["suffix"], "2023-07-01")
        checks = {"cli_identity": True, "blob": flag("finish-assets.json", "dvc_fresh_pull_passed"),
                  "container_registry": flag("finish-assets.json", "assets_ready"),
                  "managed_training": flag("finish-training-registry.json", "fresh_fit_equivalent"),
                  "model_registry": flag("finish-training-registry.json", "registry_ready"),
                  "endpoint": flag("finish-deploy.json", "api_ready"),
                  "metrics": flag("finish-monitor.json", "monitor_ready"),
                  "secret_store": (vault.get("tags") or {}).get("project") == cloud.tags["project"]}
    required = ["CLOUD_PROVIDER", "PROJECT_ID", "REGION", "BLOB_URI", "CONTAINER_REGISTRY", "MLFLOW_TRACKING_URI",
                "TRAINING_TARGET", "MODEL_REGISTRY_NAME", "ENDPOINT_NAME", "ENDPOINT_URL", "METRICS_NAMESPACE",
                "SECRET_STORE_PATH", "IDENTITY_REF", "BUDGET_LIMIT_THB"]
    return {"checks": checks, "missing_environment_values": [name for name in required if not values.get(name)],
            "passed": all(checks.values()) and all(values.get(name) for name in required),
            "limits": ["Some capability checks use saved successful runs. They do not prove unused APIs or provider swaps."]}


if __name__ == "__main__":
    report = collect()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
