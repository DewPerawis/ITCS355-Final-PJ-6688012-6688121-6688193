import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

import joblib
import numpy as np
import pandas as pd

from src.bundle import predict_profiles, save_bundle
from src.data import FEATURES, file_hash, load_splits, prepare_data, read_raw, split_profiles
from src.train import make_pipeline, run_study


def raw_sample():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["User", *FEATURES, ""])
    for i in range(30):
        writer.writerow([f"User {i}", *([i / 10] * 24), ""])
    writer.writerow(["Duplicate", *([0.5] * 24), ""])
    writer.writerow(["Bad row", *([1] * 24), "unexpected"])
    return output.getvalue().encode()


class DataTests(unittest.TestCase):
    def test_quarantine_preserves_bad_row_and_zeros(self):
        profiles, bad = read_raw(raw_sample())
        self.assertEqual(len(profiles), 31)
        self.assertEqual(profiles[0]["values"], [0.0] * 24)
        self.assertEqual(bad[0]["reason"], "unexpected extra value")
        self.assertEqual(bad[0]["raw_fields"][-1], "unexpected")

    def test_numeric_errors_are_not_repaired(self):
        for value in ["bad", "nan", "inf", "-1", "6"]:
            raw = ("User," + ",".join(FEATURES) + ",\nU," +
                   ",".join([value] + ["1"] * 23) + ",\n").encode()
            accepted, bad = read_raw(raw)
            self.assertEqual(accepted, [])
            self.assertEqual(len(bad), 1)

    def test_duplicate_groups_and_split_are_repeatable(self):
        profiles, _ = read_raw(raw_sample())
        a = split_profiles(profiles)
        b = split_profiles(list(reversed(profiles)))
        assignment = {row["csv_line"]: row["split"] for row in a}
        self.assertEqual(assignment, {row["csv_line"]: row["split"] for row in b})
        group_splits = {}
        for row in a:
            group_splits.setdefault(row["profile_hash"], set()).add(row["split"])
        self.assertTrue(all(len(splits) == 1 for splits in group_splits.values()))
        self.assertEqual({r["split"] for r in a}, {"train", "validation", "test"})

    def test_preparation_checks_hash_and_excludes_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ["configs", "reports", "data/raw"]:
                (root / name).mkdir(parents=True)
            raw = root / "data/raw/google_review_ratings.csv"
            raw.write_bytes(raw_sample())
            profiles, bad = read_raw(raw.read_bytes())
            config = {"seed": 42, "train_fraction": 0.7, "validation_fraction": 0.15,
                      "raw_sha256": file_hash(raw)}
            (root / "configs/data.json").write_text(json.dumps(config))
            audit = {"raw_sha256": file_hash(raw), "valid_rows": len(profiles), "rows": 32,
                     "invalid_rows": [{"csv_line": r["csv_line"], "reason": r["reason"]} for r in bad]}
            (root / "reports/data-audit.json").write_text(json.dumps(audit))
            prepare_data(root)
            splits, _ = load_splits(root)
            self.assertTrue(all(list(frame.columns) == FEATURES for frame in splits.values()))
            raw.write_bytes(raw.read_bytes() + b"\n")
            with self.assertRaises(ValueError):
                load_splits(root)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.train = pd.DataFrame([[0.0] * 24, [1.0] * 24, [4.0] * 24, [5.0] * 24],
                                  columns=FEATURES)

    def test_imputer_and_scaler_fit_only_training_data(self):
        pipeline = make_pipeline("zero_as_missing", 2, 42)
        pipeline.fit(self.train)
        imputer = pipeline.named_steps["imputer"]
        scaler = pipeline.named_steps["scaler"]
        np.testing.assert_allclose(imputer.statistics_, [4.0] * 24)
        means, medians = scaler.mean_.copy(), imputer.statistics_.copy()
        pipeline.predict(pd.DataFrame([[0.0] * 24, [2.0] * 24], columns=FEATURES))
        np.testing.assert_array_equal(scaler.mean_, means)
        np.testing.assert_array_equal(imputer.statistics_, medians)

    def test_predict_rejects_bad_contract_and_accepts_named_order(self):
        pipeline = make_pipeline("keep_zero", 2, 42)
        pipeline.fit(self.train)
        bundle = {"pipeline": pipeline, "mapping": {0: "A", 1: "B"},
                  "thresholds": {0: 100, 1: 100}, "version": "test"}
        expected = predict_profiles(bundle, self.train)
        self.assertEqual(expected, predict_profiles(bundle, self.train[FEATURES[::-1]]))
        invalid = [self.train.drop(columns=FEATURES[0]), self.train.assign(user_id="U"),
                   self.train.astype(str), self.train.astype(bool),
                   pd.DataFrame([[np.nan] * 24], columns=FEATURES),
                   pd.concat([self.train] * 26, ignore_index=True)]
        for frame in invalid:
            with self.assertRaises(ValueError):
                predict_profiles(bundle, frame)

    def test_study_ignores_test_data_and_bundle_reload_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ["configs", "reports", "data/raw", "src"]:
                (root / name).mkdir(parents=True)
            source_root = Path(__file__).resolve().parents[1]
            for name in ["data.py", "train.py", "bundle.py"]:
                (root / "src" / name).write_bytes((source_root / "src" / name).read_bytes())
            raw = root / "data/raw/google_review_ratings.csv"
            raw.write_bytes(raw_sample())
            accepted, bad = read_raw(raw.read_bytes())
            (root / "configs/data.json").write_text(json.dumps({
                "seed": 42, "train_fraction": 0.7, "validation_fraction": 0.15,
                "raw_sha256": file_hash(raw)}))
            (root / "reports/data-audit.json").write_text(json.dumps({
                "raw_sha256": file_hash(raw), "rows": 32, "valid_rows": len(accepted),
                "invalid_rows": [{"csv_line": row["csv_line"], "reason": row["reason"]} for row in bad]}))
            (root / "configs/study.json").write_text(json.dumps({
                "k_values": [2], "seeds": [42, 43], "zero_policies": ["keep_zero", "zero_as_missing"],
                "n_init": 2, "min_validation_cluster_fraction": 0.01, "min_stability_ari": 0.0,
                "bundle_seed": 42, "distance_quantile": 0.95}))
            prepare_data(root)
            splits, report = load_splits(root)
            poisoned = {**splits, "test": splits["test"] * np.nan}
            with patch("src.train.load_splits", return_value=(poisoned, report)), redirect_stdout(io.StringIO()):
                _, selected = run_study(root)
            self.assertTrue(selected["ready_for_bundle"])
            self.assertFalse(selected["test_used_for_selection"])
            _, manifest = save_bundle(root)
            self.assertTrue(manifest["reload_check_passed"])
            fixture = json.loads((root / "reports/golden-profiles.json").read_text())
            bundle = joblib.load(root / manifest["artifact"])
            profiles = pd.DataFrame(fixture["profiles"])
            self.assertEqual(predict_profiles(bundle, profiles), fixture["expected"])
            bundle["mapping"][0], bundle["mapping"][1] = bundle["mapping"][1], bundle["mapping"][0]
            self.assertNotEqual(predict_profiles(bundle, profiles), fixture["expected"])


if __name__ == "__main__":
    unittest.main()
