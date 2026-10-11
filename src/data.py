import csv
import hashlib
import io
import json
import math
import random
from collections import Counter

FEATURES = [f"Category {i}" for i in range(1, 25)]


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_raw(raw_bytes):
    rows = list(csv.reader(io.StringIO(raw_bytes.decode("utf-8-sig"))))
    if not rows:
        raise ValueError("The raw file is empty.")
    header = [name.strip() for name in rows[0]]
    if header[0] != "User" or len(set(header)) != len(header):
        raise ValueError("Unexpected ID column or repeated column names.")
    if not all(name in header for name in FEATURES):
        raise ValueError("The 24 rating columns are missing.")
    positions = [header.index(name) for name in FEATURES]
    extras = [i for i in range(1, len(header)) if header[i] not in FEATURES]
    accepted, quarantine = [], []
    for line, row in enumerate(rows[1:], start=2):
        reason = None
        if len(row) != len(header):
            reason = "wrong number of fields"
        elif not row[0].strip():
            reason = "missing user ID"
        elif any(row[i].strip() for i in extras):
            reason = "unexpected extra value"
        else:
            try:
                values = [float(row[i]) for i in positions]
                if not all(math.isfinite(x) for x in values):
                    reason = "missing or non-finite rating"
                elif any(x < 0 or x > 5 for x in values):
                    reason = "rating outside 0 to 5"
            except ValueError:
                reason = "non-numeric rating"
        if reason:
            quarantine.append({"csv_line": line, "reason": reason, "raw_fields": row})
        else:
            values = [0.0 if x == 0 else x for x in values]
            fingerprint = hashlib.sha256(json.dumps(values).encode()).hexdigest()
            accepted.append({"user_id": row[0].strip(), "csv_line": line,
                             "profile_hash": fingerprint, "values": values})
    return accepted, quarantine


def split_profiles(profiles, seed=42, train_fraction=0.7, validation_fraction=0.15):
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1 - train_fraction:
        raise ValueError("Split fractions must leave a non-empty test share.")
    groups = sorted({row["profile_hash"] for row in profiles})
    random.Random(seed).shuffle(groups)
    train_end = int(len(groups) * train_fraction)
    validation_end = train_end + int(len(groups) * validation_fraction)
    if not 0 < train_end < validation_end < len(groups):
        raise ValueError("Not enough unique profiles for three splits.")
    assignments = {group: ("train" if i < train_end else
                          "validation" if i < validation_end else "test")
                   for i, group in enumerate(groups)}
    return [{**row, "split": assignments[row["profile_hash"]]} for row in profiles]


def prepare_data(root):
    config_path = root / "configs/data.json"
    config = json.loads(config_path.read_text())
    raw_path = root / "data/raw/google_review_ratings.csv"
    raw_hash = file_hash(raw_path)
    if raw_hash != config["raw_sha256"]:
        raise ValueError("The raw hash differs from the reviewed version.")
    profiles, quarantine = read_raw(raw_path.read_bytes())
    audit = json.loads((root / "reports/data-audit.json").read_text())
    observed = [{"csv_line": row["csv_line"], "reason": row["reason"]} for row in quarantine]
    if (audit["raw_sha256"] != raw_hash or audit["valid_rows"] != len(profiles)
            or audit["rows"] != len(profiles) + len(quarantine)
            or audit["invalid_rows"] != observed):
        raise ValueError("The parsing result differs from Notebook 01. Review it first.")
    profiles = split_profiles(profiles, config["seed"], config["train_fraction"],
                              config["validation_fraction"])
    processed = root / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)
    with (processed / "profiles.csv").open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["user_id", "csv_line", "profile_hash", "split", *FEATURES])
        for row in profiles:
            writer.writerow([row["user_id"], row["csv_line"], row["profile_hash"],
                             row["split"], *row["values"]])
    with (processed / "quarantine.csv").open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["csv_line", "reason", "raw_fields"])
        for row in quarantine:
            writer.writerow([row["csv_line"], row["reason"], json.dumps(row["raw_fields"])])
    counts = dict(Counter(row["split"] for row in profiles))
    group_splits = {}
    for row in profiles:
        group_splits.setdefault(row["profile_hash"], set()).add(row["split"])
    crossed = sum(len(splits) > 1 for splits in group_splits.values())
    if crossed:
        raise ValueError("An identical profile crossed splits.")
    report = {"raw_sha256": raw_hash, "accepted_rows": len(profiles),
              "quarantined_rows": len(quarantine), "split_counts": counts,
              "unique_profiles": len({r["profile_hash"] for r in profiles}),
              "cross_split_duplicate_groups": crossed, "features": FEATURES, "config": config,
              "zero_policy": "unchanged; compare in Notebook 03",
              "files": {str(path.relative_to(root)): file_hash(path) for path in
                        [raw_path, config_path, processed / "profiles.csv",
                         processed / "quarantine.csv"]}}
    (root / "reports/prepared-data.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def load_splits(root):
    import pandas as pd

    report = json.loads((root / "reports/prepared-data.json").read_text())
    for name, expected in report["files"].items():
        if file_hash(root / name) != expected:
            raise ValueError(f"Changed input: {name}. Rerun Notebook 02 and later steps.")
    frame = pd.read_csv(root / "data/processed/profiles.csv")
    if frame.groupby("profile_hash")["split"].nunique().max() != 1:
        raise ValueError("An identical profile appears in different splits.")
    return {name: frame.loc[frame["split"] == name, FEATURES].reset_index(drop=True)
            for name in ["train", "validation", "test"]}, report
