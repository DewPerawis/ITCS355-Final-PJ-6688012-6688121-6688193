import argparse
import hashlib
import json
import shutil
from pathlib import Path
from importlib.metadata import version

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from threadpoolctl import threadpool_limits


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def train(profiles, package, output):
    package, output = Path(package), Path(output)
    manifest = json.loads((package / "bundle-manifest.json").read_text())
    prepared = json.loads((package / "prepared-data.json").read_text())
    selection = json.loads((package / "selection.json").read_text())
    expected = prepared["files"]["data/processed/profiles.csv"]
    if sha(profiles) != expected or sha(package / "bundle.joblib") != manifest["artifact_sha256"]:
        raise ValueError("Training input or canonical model hash differs.")
    for name, pinned in selection["packages"].items():
        if version(name) != pinned:
            raise ValueError("Training package version differs: " + name)
    frame = pd.read_csv(profiles)
    if frame.groupby("profile_hash")["split"].nunique().max() != 1:
        raise ValueError("Duplicate profiles cross splits.")
    train_data = frame.loc[frame["split"] == "train", manifest["features"]]
    canonical = joblib.load(package / "bundle.joblib")
    fitted = clone(canonical["pipeline"])
    with threadpool_limits(limits=1):
        fitted.fit(train_data)
        original = canonical["pipeline"]
        for step, attribute in [("imputer", "statistics_"), ("scaler", "mean_"),
                                ("scaler", "scale_"), ("model", "cluster_centers_")]:
            if not np.allclose(getattr(fitted.named_steps[step], attribute),
                               getattr(original.named_steps[step], attribute), rtol=1e-10, atol=1e-10):
                raise ValueError("Retraining differs from the canonical bundle: " + step)
        labels = fitted.predict(train_data)
        distances = fitted.named_steps["model"].transform(fitted[:-1].transform(train_data))
        for label, threshold in canonical["thresholds"].items():
            actual = np.quantile(distances[labels == label, label], selection["distance_quantile"])
            if not np.isclose(actual, threshold, rtol=1e-10, atol=1e-10):
                raise ValueError("Retraining changes the uncertainty threshold.")
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted, output / "retrained-pipeline.joblib")
    # Keep the tested serialization after proving that the fresh fit is equivalent.
    for name in ["bundle.joblib", "bundle-manifest.json", "golden-profiles.json"]:
        shutil.copy2(package / name, output / name)
    report = {"training_rows": len(train_data), "profiles_sha256": expected,
              "model_version": manifest["model_version"], "canonical_sha256": manifest["artifact_sha256"],
              "retrained_pipeline_sha256": sha(output / "retrained-pipeline.joblib"),
              "fresh_fit_equivalent": True, "canonical_export": True,
              "export_reason": "Preserve the tested bundle bytes after checking fresh-fit equivalence.",
              "packages": selection["packages"]}
    (output / "training-proof.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--package", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(train(args.profiles, args.package, args.output), indent=2))
