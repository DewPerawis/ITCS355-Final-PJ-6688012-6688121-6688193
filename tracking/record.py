import json
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import mlflow
import pandas as pd
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

from service.runtime import load_checked_bundle
from src.bundle import predict_profiles
from src.data import file_hash
from tracking.model import TravelModel


def record_model(root):
    root = Path(root).resolve()
    manifest_path = root / "reports/bundle-manifest.json"
    golden_path = root / "reports/golden-profiles.json"
    manifest = json.loads(manifest_path.read_text())
    bundle, _ = load_checked_bundle(root / manifest["artifact"], manifest_path, golden_path)
    if not (root / ".dvc").exists():
        subprocess.run([sys.executable, "-m", "dvc", "init"], cwd=root, check=True)
    subprocess.run([sys.executable, "-m", "dvc", "add", "data/raw"], cwd=root, check=True)
    dvc_status = subprocess.run([sys.executable, "-m", "dvc", "status", "data/raw.dvc", "--json"],
                                cwd=root, check=True, capture_output=True, text=True)
    if json.loads(dvc_status.stdout):
        raise ValueError("DVC reports changed data. Review the raw file.")
    if file_hash(root / "data/raw/google_review_ratings.csv") != manifest["raw_sha256"]:
        raise ValueError("The raw file differs from training.")
    fixture = json.loads(golden_path.read_text())
    examples = pd.DataFrame(fixture["profiles"])
    expected = pd.DataFrame(predict_profiles(bundle, examples))
    selection = json.loads((root / "reports/selection.json").read_text())
    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                              capture_output=True, text=True).stdout.strip()
    git_dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=root, check=True,
                                    capture_output=True, text=True).stdout.strip())
    uri = "sqlite:///" + (root / "mlflow.db").as_posix()
    mlflow.set_tracking_uri(uri)
    mlflow.set_registry_uri(uri)
    client = MlflowClient()
    if client.get_experiment_by_name("travel-style-segmentation") is None:
        client.create_experiment("travel-style-segmentation", artifact_location=(root / "mlartifacts").as_uri())
    experiment = mlflow.set_experiment("travel-style-segmentation")
    # Use absolute paths so artifact loading does not depend on the notebook folder.
    client.set_experiment_tag(experiment.experiment_id, "scope", "local baseline")
    packages = [f"{name}=={metadata.version(name)}" for name in
                ["mlflow", "numpy", "pandas", "scikit-learn", "scipy", "joblib", "threadpoolctl"]]
    previous_dir = Path.cwd()
    try:
        os.chdir(root)
        with mlflow.start_run(run_name=f"saved-bundle-{manifest['model_version']}") as run:
            run_id = run.info.run_id
            mlflow.set_tags({"record_type": "import of completed offline study",
                             "training_repeated": "false", "git_head": git_head,
                             "git_dirty": str(git_dirty).lower(),
                             "raw_sha256": manifest["raw_sha256"],
                             "bundle_sha256": manifest["artifact_sha256"],
                             "mapping_status": manifest["mapping_status"]})
            mlflow.log_params({"model": "kmeans", "k": manifest["k"],
                               "zero_policy": manifest["zero_policy"], "seed": selection["seed"]})
            mlflow.log_metrics({"validation_silhouette": selection["mean_silhouette"],
                                "stability_ari": selection["stability_ari"],
                                "test_silhouette": manifest["test_metrics"]["silhouette"],
                                "validation_uncertain_fraction": manifest["validation_uncertain_fraction"]})
            for name in ["data-source.json", "data-audit.json", "prepared-data.json", "selection.json",
                         "study-runs.csv", "study-summary.csv", "bundle-manifest.json", "cluster-profiles.csv"]:
                mlflow.log_artifact(str(root / "reports" / name), artifact_path="evidence")
            mlflow.log_artifact(str(root / "data/raw.dvc"), artifact_path="lineage")
            mlflow.log_artifacts(str(root / "configs"), artifact_path="configs")
            mlflow.log_artifact(str(root / "requirements-local.lock.txt"), artifact_path="environment")
            model_info = mlflow.pyfunc.log_model(
                name="model", python_model=TravelModel(),
                artifacts={"bundle": str(root / manifest["artifact"]), "manifest": str(manifest_path),
                           "golden": str(golden_path)},
                code_paths=["src", "service", "tracking"],
                signature=infer_signature(examples, expected), input_example=examples,
                pip_requirements=packages)
        registered = mlflow.register_model(model_info.model_uri, "travel-style-segmentation")
        registered_uri = f"models:/travel-style-segmentation/{registered.version}"
        reloaded = mlflow.pyfunc.load_model(registered_uri)
        actual = reloaded.predict(examples)
        pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected.reset_index(drop=True))
    finally:
        os.chdir(previous_dir)
    report = {"tracking_uri": uri, "registry_scope": "local SQLite, not Azure ML",
              "run_id": run_id, "registered_name": registered.name,
              "registered_version": registered.version, "model_uri": registered_uri,
              "bundle_version": manifest["model_version"], "bundle_sha256": manifest["artifact_sha256"],
              "raw_sha256": manifest["raw_sha256"], "dvc_pointer_sha256": file_hash(root / "data/raw.dvc"),
              "dvc_status_clean": True, "registry_reload_passed": True,
              "training_repeated": False, "cloud_uploaded": False,
              "git_head": git_head, "git_dirty": git_dirty}
    (root / "reports/local-registry.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
