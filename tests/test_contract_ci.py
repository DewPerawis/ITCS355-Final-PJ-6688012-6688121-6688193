import json
import os
import platform
import tempfile
import unittest
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from threadpoolctl import threadpool_limits

from service.app import create_app
from src.bundle import predict_profiles
from src.data import FEATURES, file_hash
from src.train import make_pipeline


class ContractTests(unittest.TestCase):
    def test_prediction_contract_with_an_isolated_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            frame = pd.DataFrame(np.random.default_rng(42).uniform(0, 5, (40, 24)), columns=FEATURES)
            with threadpool_limits(limits=1):
                model = make_pipeline("keep_zero", 2, 42).fit(frame)
            bundle = {"pipeline": model, "features": FEATURES, "zero_policy": "keep_zero",
                      "mapping": {0: "Segment 1", 1: "Segment 2"}, "thresholds": {0: 100.0, 1: 100.0},
                      "version": "synthetic-test", "mapping_status": "test fixture"}
            path = root / "bundle.joblib"
            joblib.dump(bundle, path)
            manifest = {"artifact": "bundle.joblib", "artifact_sha256": file_hash(path), "python": platform.python_version(),
                        "packages": {name: version(name) for name in ["numpy", "pandas", "scikit-learn", "joblib"]},
                        "k": 2, "model_version": bundle["version"], "mapping": bundle["mapping"],
                        "thresholds": bundle["thresholds"], "zero_policy": "keep_zero"}
            golden = frame.iloc[:3]
            fixture = {"artifact_sha256": manifest["artifact_sha256"], "profiles": golden.to_dict(orient="records"),
                       "expected": predict_profiles(bundle, golden)}
            (root / "reports/bundle-manifest.json").write_text(json.dumps(manifest))
            (root / "reports/golden-profiles.json").write_text(json.dumps(fixture))
            with TestClient(create_app(root)) as client:
                self.assertEqual(client.get("/ready").status_code, 200)
                self.assertEqual(client.get("/canary").status_code, 200)
                self.assertEqual(client.post("/predict", json={"profiles": fixture["profiles"]}).status_code, 200)
                self.assertEqual(client.post("/predict", json={"profiles": [{"Category 1": 2}]}).status_code, 422)
                self.assertEqual(client.post("/predict", json={"profiles": [fixture["profiles"][0]] * 101}).status_code, 422)

    def test_demo_gate(self):
        self.assertNotEqual(os.environ.get("DEMO_FAIL", "false").lower(), "true",
                            "Deliberate CI test failure: the deployment job must be skipped.")


if __name__ == "__main__":
    unittest.main()
