import hashlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from cloudlayer.platform_deploy import check_preview


class DeployTests(unittest.TestCase):
    def test_changed_files_cannot_be_applied(self):
        with tempfile.TemporaryDirectory() as directory:
            template, parameters = Path(directory) / "template.json", Path(directory) / "parameters.json"
            template.write_text("{}")
            parameters.write_text("{}")
            digest = hashlib.sha256(b"{}").hexdigest()
            report = {"errors": [], "preview_ready": True, "validation_passed": True,
                      "changes": [{"change": "Create"}], "template_sha256": digest,
                      "parameters_sha256": digest, "checked_at": datetime.now(timezone.utc).isoformat()}
            check_preview(report, template, parameters)
            template.write_text('{"changed":true}')
            with self.assertRaises(ValueError):
                check_preview(report, template, parameters)

    def test_delete_preview_cannot_be_applied(self):
        report = {"errors": [], "preview_ready": True, "validation_passed": True,
                  "changes": [{"change": "Delete"}]}
        with self.assertRaises(ValueError):
            check_preview(report, Path("unused"), Path("unused"))


if __name__ == "__main__":
    unittest.main()
