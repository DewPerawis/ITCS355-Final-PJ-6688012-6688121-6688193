import json
import shutil
import tempfile
import unittest
from pathlib import Path

from service.runtime import load_checked_bundle

ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def test_saved_bundle_and_golden_profiles_match(self):
        manifest_path = ROOT / "reports/bundle-manifest.json"
        if not manifest_path.exists():
            self.skipTest("Run Notebook 04 first.")
        manifest = json.loads(manifest_path.read_text())
        bundle, _ = load_checked_bundle(ROOT / manifest["artifact"], manifest_path,
                                        ROOT / "reports/golden-profiles.json")
        self.assertEqual(bundle["version"], manifest["model_version"])

    def test_changed_artifact_is_rejected_before_loading(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            artifact = root / "bundle.joblib"
            artifact.write_bytes(b"changed content")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"artifact_sha256": "0" * 64}))
            with self.assertRaisesRegex(ValueError, "hash"):
                load_checked_bundle(artifact, manifest)

    def test_changed_mapping_is_rejected(self):
        path = ROOT / "reports/bundle-manifest.json"
        if not path.exists():
            self.skipTest("Run Notebook 04 first.")
        with tempfile.TemporaryDirectory() as folder:
            manifest = json.loads(path.read_text())
            manifest["mapping"]["0"], manifest["mapping"]["1"] = manifest["mapping"]["1"], manifest["mapping"]["0"]
            altered = Path(folder) / "manifest.json"
            altered.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "mapping"):
                load_checked_bundle(ROOT / manifest["artifact"], altered)


if __name__ == "__main__":
    unittest.main()
