import json
import math
import platform
from importlib import metadata
from pathlib import Path

import joblib
import pandas as pd

from src.bundle import predict_profiles
from src.data import FEATURES, file_hash


def load_checked_bundle(artifact, manifest_path, golden_path=None):
    manifest = json.loads(Path(manifest_path).read_text())
    if file_hash(Path(artifact)) != manifest["artifact_sha256"]:
        raise ValueError("Bundle hash does not match the manifest.")
    if platform.python_version().split(".")[:2] != manifest["python"].split(".")[:2]:
        raise ValueError("Python major/minor version differs from training.")
    for name, expected in manifest["packages"].items():
        if metadata.version(name) != expected:
            raise ValueError(f"Runtime package differs from training: {name}")
    bundle = joblib.load(artifact)
    k = manifest["k"]
    if bundle["version"] != manifest["model_version"] or bundle["features"] != FEATURES:
        raise ValueError("Model version or feature order differs.")
    if bundle["zero_policy"] != manifest["zero_policy"]:
        raise ValueError("Zero policy differs.")
    if set(bundle["mapping"]) != set(range(k)) or len(set(bundle["mapping"].values())) != k:
        raise ValueError("Segment mapping is incomplete or repeated.")
    if bundle["mapping"] != {int(i): name for i, name in manifest["mapping"].items()}:
        raise ValueError("Segment mapping differs from the manifest.")
    if bundle["thresholds"] != {int(i): value for i, value in manifest["thresholds"].items()}:
        raise ValueError("Distance thresholds differ.")
    if any(not math.isfinite(x) or x < 0 for x in bundle["thresholds"].values()):
        raise ValueError("Distance thresholds are invalid.")
    if bundle["pipeline"].named_steps["model"].cluster_centers_.shape != (k, len(FEATURES)):
        raise ValueError("Model shape differs from the schema.")
    if golden_path is not None:
        fixture = json.loads(Path(golden_path).read_text())
        if fixture["artifact_sha256"] != manifest["artifact_sha256"]:
            raise ValueError("Golden fixture belongs to another artifact.")
        if predict_profiles(bundle, pd.DataFrame(fixture["profiles"])) != fixture["expected"]:
            raise ValueError("Golden predictions differ.")
    return bundle, manifest
