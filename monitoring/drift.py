import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from cloudlayer.blob_sync import digest

ROOT = Path(__file__).resolve().parents[1]


def score(reference, recent):
    if len(reference) < 200 or len(recent) != 200:
        raise ValueError("Use at least 200 reference rows and exactly 200 recent rows.")
    return float(np.max(ks_2samp(reference, recent, axis=0).statistic))


def evaluate(train, recent, rounds=100, seed=42):
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(train))
    reference, pool = train[order[:len(train)//2]], train[order[len(train)//2:]]
    if len(pool) < 200 or len(recent) < 200:
        raise ValueError("Not enough rows for drift calibration.")
    null = [score(reference, pool[rng.choice(len(pool), 200, replace=False)]) for _ in range(rounds)]
    threshold = float(np.quantile(null, .95))
    window = recent[rng.choice(len(recent), 200, replace=False)].copy()
    shifted = window.copy()
    shifted[:, :4] = np.clip(shifted[:, :4] + 1.5, 0, 5)
    normal, injected = score(reference, window), score(reference, shifted)
    return {"method": "Maximum feature-wise two-sample KS statistic",
            "reference_rows": len(reference), "recent_rows": 200, "calibration_rounds": rounds,
            "threshold": threshold, "normal_score": normal, "normal_flagged": normal > threshold,
            "injected_score": injected, "injected_detected": injected > threshold,
            "injection": "Add 1.5 to the first four feature ratings, clipped to [0,5]",
            "seed": seed,
            "limits": ["Controlled input drift demonstration, not observed temporal drift.",
                       "Threshold is calibrated on training windows; the normal holdout may still be flagged.",
                       "The dataset has no timestamps or outcome labels. This does not prove concept drift.",
                       "This offline check is not a live rolling-window monitor."]}


def main():
    prepared = json.loads((ROOT / "reports/prepared-data.json").read_text())
    path = ROOT / "data/processed/profiles.csv"
    if digest(path) != prepared["files"]["data/processed/profiles.csv"]:
        raise ValueError("Processed data changed.")
    manifest = json.loads((ROOT / "reports/bundle-manifest.json").read_text())
    frame = pd.read_csv(path)
    features = manifest["features"]
    result = evaluate(frame.loc[frame.split == "train", features].to_numpy(),
                      frame.loc[frame.split == "test", features].to_numpy())
    result["verified"] = result["injected_detected"]
    result["processed_sha256"] = digest(path)
    (ROOT / "reports/input-drift.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["injected_detected"]:
        raise RuntimeError("Controlled drift was not detected. Review the report; do not claim a pass.")


if __name__ == "__main__":
    main()
