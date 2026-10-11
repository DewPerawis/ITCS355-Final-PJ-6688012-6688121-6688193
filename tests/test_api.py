import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from importlib.util import find_spec

from service.runtime import load_checked_bundle
from src.data import FEATURES

API_AVAILABLE = find_spec("fastapi") is not None and find_spec("httpx") is not None
if API_AVAILABLE:
    from fastapi.testclient import TestClient
    from service.app import create_app

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(API_AVAILABLE, "Run setup_local.sh for API checks.")
class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "reports/bundle-manifest.json").exists():
            raise unittest.SkipTest("Run Notebook 04 first.")
        fixture = json.loads((ROOT / "reports/golden-profiles.json").read_text())
        cls.profiles, cls.expected = fixture["profiles"], fixture["expected"]

    def test_golden_predictions_and_uncertain_response(self):
        with TestClient(create_app(ROOT)) as client:
            self.assertEqual(client.get("/health").status_code, 200)
            self.assertEqual(client.get("/ready").status_code, 200)
            response = client.post("/predict", json={"profiles": self.profiles})
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(response.headers["X-Request-ID"], body["request_id"])
            for actual, expected in zip(body["predictions"], self.expected):
                self.assertEqual(actual["cluster_id"], expected["cluster_id"])
                self.assertEqual(actual["model_version"], expected["model_version"])
                self.assertAlmostEqual(actual["distance"], expected["distance"])
                self.assertEqual(actual["uncertain"], expected["uncertain"])
                self.assertEqual(actual["segment"], None if expected["uncertain"] else expected["segment"])

    def test_bad_requests_are_422(self):
        profile = self.profiles[0]
        missing = {key: value for key, value in profile.items() if key != FEATURES[0]}
        invalid = [{"profiles": []}, {"profiles": [profile] * 101},
                   {"profiles": [missing]}, {"profiles": [{**profile, "extra": 1}]},
                   {"profiles": [{**profile, FEATURES[0]: "2"}]},
                   {"profiles": [{**profile, FEATURES[0]: True}]},
                   {"profiles": [{**profile, FEATURES[0]: -1}]},
                   {"profiles": [{**profile, FEATURES[0]: 6}]},
                   {"profiles": [profile], "extra": 1}]
        with TestClient(create_app(ROOT)) as client:
            for body in invalid:
                self.assertEqual(client.post("/predict", json=body).status_code, 422)
            for value in ["NaN", "Infinity", "-Infinity"]:
                body = json.dumps({"profiles": [{**profile, FEATURES[0]: 0.0}]}).replace(
                    '"Category 1": 0.0', '"Category 1": ' + value)
                self.assertEqual(client.post("/predict", content=body,
                                             headers={"Content-Type": "application/json"}).status_code, 422)

    def test_batch_100_and_current_input(self):
        with TestClient(create_app(ROOT)) as client:
            response = client.post("/predict", json={"profiles": [self.profiles[0]] * 100})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()["predictions"]), 100)
            for i in [0, 1]:
                row = client.post("/predict", json={"profiles": [self.profiles[i]]}).json()["predictions"][0]
                self.assertEqual(row["cluster_id"], self.expected[i]["cluster_id"])

    def test_failed_model_load_keeps_health_but_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as folder:
            # This test expects a missing model and checks its error log.
            with self.assertLogs("mlop_api", level="ERROR") as captured:
                with TestClient(create_app(folder)) as client:
                    self.assertEqual(client.get("/health").status_code, 200)
                    self.assertEqual(client.get("/ready").status_code, 503)
                    self.assertEqual(client.post("/predict", json={"profiles": self.profiles}).status_code, 503)
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(captured.records[0].getMessage(), "Model load failed.")
            self.assertIsInstance(captured.records[0].exc_info[1], FileNotFoundError)

    def test_bundle_loads_once_per_start(self):
        with patch("service.app.load_checked_bundle", wraps=load_checked_bundle) as loader:
            with TestClient(create_app(ROOT)) as client:
                for _ in range(3):
                    self.assertEqual(client.post("/predict", json={"profiles": self.profiles}).status_code, 200)
            self.assertEqual(loader.call_count, 1)

    def test_semantic_canary_detects_staging_mapping_failure(self):
        with TestClient(create_app(ROOT)) as client:
            self.assertEqual(client.get("/canary").status_code, 200)
        with patch.dict("os.environ", {"DEPLOYMENT_STAGE": "staging", "MLOP_FAILURE_MODE": "wrong_mapping"}):
            with TestClient(create_app(ROOT)) as client:
                self.assertEqual(client.get("/ready").status_code, 200)
                self.assertEqual(client.get("/canary").status_code, 503)

    def test_failure_injection_is_blocked_outside_staging(self):
        with patch.dict("os.environ", {"DEPLOYMENT_STAGE": "production", "MLOP_FAILURE_MODE": "wrong_mapping"}):
            with self.assertLogs("mlop_api", level="ERROR"):
                with TestClient(create_app(ROOT)) as client:
                    self.assertEqual(client.get("/ready").status_code, 503)


if __name__ == "__main__":
    unittest.main()
