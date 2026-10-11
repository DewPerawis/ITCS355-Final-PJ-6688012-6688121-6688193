import itertools
import json
import platform
import time
from importlib import metadata

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from threadpoolctl import threadpool_limits

from src.data import file_hash, load_splits


def zeros_to_nan(values):
    values = np.asarray(values, dtype=float).copy()
    values[values == 0] = np.nan
    return values


def make_pipeline(policy, k, seed, n_init=10, model_type="kmeans"):
    if policy not in {"keep_zero", "zero_as_missing"}:
        raise ValueError("Unknown zero policy.")
    zero_step = FunctionTransformer(zeros_to_nan if policy == "zero_as_missing" else None)
    if model_type == "kmeans":
        model = KMeans(n_clusters=k, random_state=seed, n_init=n_init)
    elif model_type == "gmm":
        model = GaussianMixture(n_components=k, covariance_type="diag", random_state=seed,
                                n_init=3, max_iter=300)
    else:
        raise ValueError("Unknown model type.")
    return Pipeline([("zeros", zero_step),
                     ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                     ("scaler", StandardScaler()), ("model", model)])


def cluster_metrics(transformed, labels, k):
    unique = np.unique(labels)
    valid = 1 < len(unique) < len(labels)
    counts = np.bincount(labels, minlength=k)
    return {"silhouette": float(silhouette_score(transformed, labels)) if valid else None,
            "davies_bouldin": float(davies_bouldin_score(transformed, labels)) if valid else None,
            "min_cluster_fraction": float(counts.min() / len(labels)),
            "cluster_counts": counts.tolist()}


def run_study(root):
    config_path = root / "configs/study.json"
    config = json.loads(config_path.read_text())
    splits, prepared = load_splits(root)
    train, validation = splits["train"], splits["validation"]
    if len(config["seeds"]) < 2 or len(set(config["seeds"])) != len(config["seeds"]):
        raise ValueError("Use at least two different seeds for stability.")
    if not all(1 < k < len(train) for k in config["k_values"]):
        raise ValueError("Cluster counts must fit the training set.")
    runs, summaries = [], []
    total = len(config["zero_policies"]) * len(config["k_values"]) * len(config["seeds"])
    with threadpool_limits(limits=1):
        for policy in config["zero_policies"]:
            for k in config["k_values"]:
                predictions, group_runs = [], []
                for seed in config["seeds"]:
                    started = time.perf_counter()
                    pipeline = make_pipeline(policy, k, seed, config["n_init"])
                    pipeline.fit(train)
                    transformed = pipeline[:-1].transform(validation)
                    labels = pipeline.predict(validation)
                    metrics = cluster_metrics(transformed, labels, k)
                    run = {"zero_policy": policy, "k": k, "seed": seed, **metrics,
                           "seconds": time.perf_counter() - started}
                    runs.append(run)
                    group_runs.append(run)
                    predictions.append(labels)
                    print(f"Run {len(runs)}/{total}: {policy}, k={k}, seed={seed}", flush=True)
                scores = [adjusted_rand_score(a, b)
                          for a, b in itertools.combinations(predictions, 2)]
                usable = all(r["silhouette"] is not None for r in group_runs)
                summary = {"zero_policy": policy, "k": k,
                           "mean_silhouette": float(np.mean([r["silhouette"] for r in group_runs]))
                           if usable else None,
                           "stability_ari": float(np.mean(scores)),
                           "min_cluster_fraction": min(r["min_cluster_fraction"] for r in group_runs)}
                summary["eligible"] = bool(usable and
                    summary["stability_ari"] >= config["min_stability_ari"] and
                    summary["min_cluster_fraction"] >= config["min_validation_cluster_fraction"])
                summaries.append(summary)
        candidates = [s for s in summaries if s["mean_silhouette"] is not None]
        if not candidates:
            raise ValueError("No usable clustering result. Review the data and settings.")
        eligible = [s for s in candidates if s["eligible"]]
        ranked = sorted(eligible or candidates, key=lambda s:
                        (-s["mean_silhouette"], -s["stability_ari"], s["k"], s["zero_policy"]))
        best = ranked[0]
        comparator = make_pipeline(best["zero_policy"], best["k"], config["bundle_seed"],
                                   model_type="gmm")
        comparator.fit(train)
        gmm_metrics = cluster_metrics(comparator[:-1].transform(validation),
                                      comparator.predict(validation), best["k"])
        gmm_metrics["converged"] = bool(comparator.named_steps["model"].converged_)
    selection = {"model_type": "kmeans", **best, "seed": config["bundle_seed"],
                 "n_init": config["n_init"], "distance_quantile": config["distance_quantile"],
                 "ready_for_bundle": bool(eligible), "gmm_comparison": gmm_metrics,
                 "raw_sha256": prepared["raw_sha256"],
                 "prepared_report_sha256": file_hash(root / "reports/prepared-data.json"),
                 "study_config_sha256": file_hash(config_path),
                 "code_sha256": {name: file_hash(root / name) for name in
                                  ["src/data.py", "src/train.py", "src/bundle.py"]},
                 "selection_rule": f"ARI >= {config['min_stability_ari']} and each validation cluster >= "
                                   f"{config['min_validation_cluster_fraction']:.0%}; then highest mean silhouette",
                 "python": platform.python_version(),
                 "packages": {name: metadata.version(name) for name in
                              ["numpy", "pandas", "scikit-learn", "joblib", "scipy"]},
                 "test_used_for_selection": False,
                 "zero_meaning": "unknown; this is a representation comparison"}
    pd.DataFrame(runs).to_csv(root / "reports/study-runs.csv", index=False)
    pd.DataFrame(summaries).to_csv(root / "reports/study-summary.csv", index=False)
    (root / "reports/selection.json").write_text(json.dumps(selection, indent=2, allow_nan=False) + "\n")
    return pd.DataFrame(summaries).sort_values("mean_silhouette", ascending=False), selection
