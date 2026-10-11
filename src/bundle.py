import hashlib
import json
import platform
from importlib import metadata

import joblib
import numpy as np
from threadpoolctl import threadpool_limits

from src.data import FEATURES, file_hash, load_splits
from src.train import cluster_metrics, make_pipeline


def predict_profiles(bundle, profiles, thread_controller=None):
    import pandas as pd

    if (not isinstance(profiles, pd.DataFrame) or not profiles.columns.is_unique
            or set(profiles.columns) != set(FEATURES)):
        raise ValueError("Provide exactly the 24 named rating columns.")
    if not 1 <= len(profiles) <= 100:
        raise ValueError("Batch size must be between 1 and 100.")
    if not all(pd.api.types.is_numeric_dtype(dtype) and not pd.api.types.is_bool_dtype(dtype)
               for dtype in profiles.dtypes):
        raise ValueError("Ratings must be numeric, not strings or booleans.")
    values = profiles[FEATURES].to_numpy(dtype=float)
    if not np.isfinite(values).all() or ((values < 0) | (values > 5)).any():
        raise ValueError("Ratings must be finite and between 0 and 5.")
    pipeline = bundle["pipeline"]
    ordered = profiles[FEATURES]
    limit = threadpool_limits(limits=1) if thread_controller is None else thread_controller.limit(limits=1)
    with limit:
        transformed = pipeline[:-1].transform(ordered)
        model = pipeline.named_steps["model"]
        labels = model.predict(transformed)
        distances = model.transform(transformed)
    return [{"cluster_id": int(label), "segment": bundle["mapping"][int(label)],
             "distance": float(distances[i, label]),
             "uncertain": bool(distances[i, label] > bundle["thresholds"][int(label)]),
             "model_version": bundle["version"]}
            for i, label in enumerate(labels)]


def save_bundle(root):
    selection_path = root / "reports/selection.json"
    selection = json.loads(selection_path.read_text())
    if not selection["ready_for_bundle"]:
        raise ValueError("The study did not meet the size/stability checks. Review Notebook 03.")
    if platform.python_version() != selection["python"] or any(
            metadata.version(name) != version for name, version in selection["packages"].items()):
        raise ValueError("The training environment changed. Rerun Notebook 03.")
    if file_hash(root / "reports/prepared-data.json") != selection["prepared_report_sha256"]:
        raise ValueError("Prepared data changed. Rerun Notebook 03.")
    if file_hash(root / "configs/study.json") != selection["study_config_sha256"]:
        raise ValueError("Study settings changed. Rerun Notebook 03.")
    for name, expected in selection["code_sha256"].items():
        if file_hash(root / name) != expected:
            raise ValueError(f"Code changed: {name}. Rerun Notebook 03.")
    splits, prepared = load_splits(root)
    train, validation, test = (splits[name] for name in ["train", "validation", "test"])
    pipeline = make_pipeline(selection["zero_policy"], selection["k"],
                             selection["seed"], selection["n_init"])
    k = selection["k"]
    with threadpool_limits(limits=1):
        pipeline.fit(train)
        labels = pipeline.predict(train)
        transformed = pipeline[:-1].transform(train)
        distances = pipeline.named_steps["model"].transform(transformed)
        if len(np.unique(labels)) != k:
            raise ValueError("The final fit has an empty cluster.")
        thresholds = {i: float(np.quantile(distances[labels == i, i], selection["distance_quantile"]))
                      for i in range(k)}
        test_labels = pipeline.predict(test)
        test_metrics = cluster_metrics(pipeline[:-1].transform(test), test_labels, k)
    version = hashlib.sha256(selection_path.read_bytes()).hexdigest()[:12]
    bundle = {"pipeline": pipeline, "features": FEATURES, "zero_policy": selection["zero_policy"],
              "mapping": {i: f"Segment {i + 1}" for i in range(k)}, "thresholds": thresholds,
              "version": version, "mapping_status": "provisional; review the cluster profiles"}
    folder = root / "models/artifacts" / version
    folder.mkdir(parents=True, exist_ok=True)
    artifact = folder / "bundle.joblib"
    joblib.dump(bundle, artifact)
    loaded = joblib.load(artifact)
    golden = train.iloc[[np.flatnonzero(labels == i)[0] for i in range(k)]].copy()
    before, after = predict_profiles(bundle, golden), predict_profiles(loaded, golden)
    if before != after:
        raise ValueError("Reloaded bundle predictions changed.")
    for i, row in enumerate(before):
        if row["cluster_id"] != i:
            raise ValueError("Golden profile does not match its cluster.")
    filled_train = pipeline[:2].transform(train)
    import pandas as pd
    profiles = pd.DataFrame(filled_train, columns=FEATURES).assign(cluster_id=labels)
    means = profiles.groupby("cluster_id").mean().round(3)
    means.to_csv(root / "reports/cluster-profiles.csv")
    validation_uncertain = np.mean([row["uncertain"] for start in range(0, len(validation), 100)
                                    for row in predict_profiles(bundle, validation.iloc[start:start + 100])])
    manifest = {"model_version": version, "artifact": str(artifact.relative_to(root)),
                "artifact_sha256": file_hash(artifact), "raw_sha256": prepared["raw_sha256"],
                "selection_sha256": file_hash(selection_path), "features": FEATURES,
                "zero_policy": selection["zero_policy"], "k": k, "mapping": bundle["mapping"],
                "mapping_status": bundle["mapping_status"], "thresholds": thresholds,
                "threshold_rule": f"per-cluster training distance {selection['distance_quantile']:.0%} "
                                  "quantile; not a probability",
                "validation_uncertain_fraction": float(validation_uncertain),
                "test_metrics": test_metrics, "reload_check_passed": True,
                "python": platform.python_version(), "packages": {name: metadata.version(name)
                    for name in ["numpy", "pandas", "scikit-learn", "joblib"]},
                "registry_uploaded": False, "deployed": False}
    (root / "reports/bundle-manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    fixture = {"model_version": version, "artifact_sha256": manifest["artifact_sha256"],
               "profiles": golden.to_dict(orient="records"), "expected": after}
    (root / "reports/golden-profiles.json").write_text(json.dumps(fixture, indent=2) + "\n")
    return means, manifest
