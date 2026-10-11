import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cloudlayer.blob_sync import digest, files_for, upload


class BlobTests(unittest.TestCase):
    def prepare(self, root):
        for name in ["reports", "configs", "data/raw", "data/processed", "models"]:
            (root / name).mkdir(parents=True, exist_ok=True)
        for name in ["data/raw/ratings.csv", "data/processed/profiles.csv", "configs/data.json",
                     "models/bundle.joblib", "data/raw.dvc"]:
            (root / name).write_text("sample")
        raw = digest(root / "data/raw/ratings.csv")
        values = {"data-source.json": {"raw_file": "data/raw/ratings.csv", "sha256": raw},
                  "bundle-manifest.json": {"artifact": "models/bundle.joblib", "artifact_sha256": raw,
                                           "raw_sha256": raw},
                  "prepared-data.json": {"raw_sha256": raw, "files": {
                      "data/processed/profiles.csv": raw, "configs/data.json": raw}}}
        for name, value in values.items():
            (root / "reports" / name).write_text(json.dumps(value))

    def test_changed_pinned_data_stops_before_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            self.assertEqual(len(files_for(root)), 7)
            (root / "data/raw/ratings.csv").write_text("changed")
            with self.assertRaises(ValueError):
                files_for(root)

    def test_lineage_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            path = root / "reports/bundle-manifest.json"
            value = json.loads(path.read_text())
            value["raw_sha256"] = "different"
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                files_for(root)

    @patch("cloudlayer.blob_sync.connect")
    @patch("cloudlayer.blob_sync.files_for")
    def test_existing_blob_is_checked_without_overwrite(self, files, connect):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            (root / "sample.txt").write_text("sample")
            (root / "reports/azure-blob-access.json").write_text(json.dumps({
                "errors": [], "blob_access_ready": True, "resource_group": "test", "region": "centralindia"}))
            row = {"file": "sample.txt", "sha256": digest(root / "sample.txt"), "blob": "snapshot"}
            files.return_value = [row]
            calls = []
            def run(args):
                calls.append(args)
                if args[:3] == ["storage", "blob", "exists"]:
                    return {"exists": True}
                if args[:3] == ["storage", "blob", "download"]:
                    Path(args[args.index("--file") + 1]).write_text("sample")
                    return {}
                self.fail("Unexpected cloud operation")
            connect.return_value = (run, {"resource_group": "test", "region": "centralindia"}, "scope", [])
            report = {}
            upload(root, report, {})
            self.assertTrue(report["all_hashes_match"])
            self.assertFalse(report["files"][0]["uploaded_now"])
            self.assertFalse(any(args[:3] == ["storage", "blob", "upload"] for args in calls))


if __name__ == "__main__":
    unittest.main()
