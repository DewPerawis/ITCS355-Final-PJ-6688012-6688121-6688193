import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bundle import save_bundle
from src.data import file_hash, prepare_data, read_raw
from src.train import run_study


def audit():
    raw = ROOT / "data/raw/google_review_ratings.csv"
    config = json.loads((ROOT / "configs/data.json").read_text())
    if file_hash(raw) != config["raw_sha256"]:
        raise ValueError("Raw data differs from the pinned version.")
    profiles, bad = read_raw(raw.read_bytes())
    report = {"raw_sha256": file_hash(raw), "rows": len(profiles) + len(bad),
              "valid_rows": len(profiles), "invalid_rows": [
                  {"csv_line": row["csv_line"], "reason": row["reason"]} for row in bad],
              "feature_count": 24, "zero_values": sum(v == 0 for row in profiles for v in row["values"]),
              "duplicate_profiles": len(profiles) - len({row["profile_hash"] for row in profiles}),
              "zero_policy": "not decided", "cleaned_dataset_saved": False}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/data-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce the local project stages.")
    parser.add_argument("stage", choices=["audit", "prepare", "study", "bundle", "all"])
    stage = parser.parse_args().stage
    steps = {"audit": audit, "prepare": lambda: prepare_data(ROOT),
             "study": lambda: run_study(ROOT)[1], "bundle": lambda: save_bundle(ROOT)[1]}
    for name in (steps if stage == "all" else [stage]):
        print(name, json.dumps(steps[name](), indent=2))
