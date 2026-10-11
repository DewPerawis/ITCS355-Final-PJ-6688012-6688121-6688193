import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from cloudlayer.preflight import read_azure

CONTAINERAPP_VERSION = "1.3.0b5"


def change(args, report, label):
    try:
        result = subprocess.run(["az", *args, "--only-show-errors", "-o", "none"],
                                capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            report["changes"].append(label)
            return
        codes = re.findall(r"\(([A-Za-z][A-Za-z0-9]+)\)", result.stderr)
        report["errors"].append({"step": label, "code": codes[0] if codes else "CLIError",
                                 "return_code": result.returncode})
    except (OSError, subprocess.TimeoutExpired) as error:
        report["errors"].append({"step": label, "code": type(error).__name__})


def collect(status_only=False):
    failed = []
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "changes": [],
              "errors": [], "checks_failed": failed, "resources_created": False,
              "status_only": status_only, "setup_ready": False,
              "requested_containerapp_version": CONTAINERAPP_VERSION}
    account = read_azure(["account", "show", "--query", "{state:state}"], failed, "account")
    if not account or account.get("state") != "Enabled":
        failed.append("subscription_not_enabled")
        return report
    extensions = read_azure(["extension", "list", "--query", "[].name"], failed, "extensions")
    provider = read_azure(["provider", "show", "--namespace", "Microsoft.App",
                           "--query", "{state:registrationState}"], failed, "Microsoft.App")
    if failed:
        return report
    if not status_only:
        if "containerapp" not in extensions:
            # This CLI extension is published as preview, including older versions.
            change(["extension", "add", "--name", "containerapp", "--version", CONTAINERAPP_VERSION,
                    "--allow-preview", "true", "--yes"],
                   report, "install_containerapp_extension")
        if provider.get("state") in {"NotRegistered", "Unregistered"}:
            change(["provider", "register", "--namespace", "Microsoft.App"],
                   report, "register_Microsoft.App")
        extensions = read_azure(["extension", "list", "--query", "[].name"], failed, "extensions_after")
        provider = read_azure(["provider", "show", "--namespace", "Microsoft.App",
                               "--query", "{state:registrationState}"], failed, "Microsoft.App_after")
    report["extensions"] = extensions
    report["provider_state"] = (provider or {}).get("state")
    report["setup_ready"] = (not failed and not report["errors"]
                             and "containerapp" in (extensions or [])
                             and report["provider_state"] == "Registered")
    report["next"] = ("Review prices, permissions, and service quota before deployment."
                      if report["setup_ready"] else "Read status again if Registering; stop on errors.")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-only", action="store_true")
    args = parser.parse_args()
    report = collect(args.status_only)
    root = Path(__file__).resolve().parents[1]
    (root / "reports/azure-tools.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
