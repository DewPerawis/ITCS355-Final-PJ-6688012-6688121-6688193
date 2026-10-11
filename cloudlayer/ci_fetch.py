import os
from pathlib import Path

from cloudlayer.blob_sync import digest
from cloudlayer.session import ROOT, Session, read


def fetch():
    rows = read("reports/azure-blob-upload.json")["files"]
    needed = {read("reports/bundle-manifest.json")["artifact"]}
    with Session() as cloud:
        if os.environ.get("STORAGE_ACCOUNT") != cloud.storage:
            raise ValueError("Workflow storage account differs from the project.")
        for row in rows:
            if row["file"] not in needed:
                continue
            destination = ROOT / row["file"]
            if not destination.resolve().is_relative_to(ROOT.resolve()):
                raise ValueError("Artifact path is outside the project.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            cloud.az(["storage", "blob", "download", "--account-name", cloud.storage,
                      "--container-name", "mlop-data", "--name", row["blob"], "--file", str(destination),
                      "--auth-mode", "login", "--overwrite", "false", "--query", "{name:name}"])
            if digest(destination) != row["sha256"]:
                raise ValueError("CI model download hash differs.")


if __name__ == "__main__":
    fetch()
