import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from cloudlayer.platform_preview import PROJECT, azure, check_group, plan_for
from cloudlayer.platform_verify import has_role


ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text())


def write(name, value):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def command(args, label, cwd=ROOT, env=None, timeout=1200):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        log = ROOT / "tmp" / (re.sub(r"[^a-z0-9-]", "-", label.lower()) + ".log")
        log.parent.mkdir(exist_ok=True)
        log.write_text(result.stdout + result.stderr)
        raise RuntimeError(label + " failed. Details are in the local tmp log.")
    return result.stdout


class Session:
    def __enter__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mlop-finish-cli-")
        self.env = dict(os.environ, AZURE_EXTENSION_DIR=self.temp.name)
        self.account = azure(["account", "show", "--query", "{id:id,tenantId:tenantId,state:state}"], self.env)
        if self.account["state"] != "Enabled":
            raise ValueError("Subscription is not enabled.")
        self.plan = plan_for(self.account, read("configs/azure.json"))
        self.group = self.plan["resource_group"]
        self.region = self.plan["region"]
        group = self.az(["group", "show", "--name", self.group, "--query", "{location:location,tags:tags}"])
        check_group(group, self.plan)
        deadline = group["tags"].get("removeAfter")
        if not deadline or datetime.fromisoformat(deadline) <= datetime.now(timezone.utc):
            raise ValueError("Cleanup reminder has passed. Review costs before creating more resources.")
        self.tags = {"project": PROJECT, "course": "itcs355", "student": "6688012", "lab": "capstone", "removeAfter": deadline}
        self.base = f'https://management.azure.com/subscriptions/{self.account["id"]}/resourceGroups/{self.group}/providers/'
        suffix = self.plan["suffix"]
        self.storage = "stmloppj" + suffix
        self.registry = "acrmloppj" + suffix
        self.host = self.registry + ".azurecr.io"
        self.workspace = "ml-mlop-pj-" + suffix
        self.app = "travel-style-" + suffix
        self.environment = "cae-mlop-pj-" + suffix
        return self

    def __exit__(self, *args):
        if hasattr(self, "ml_temp"):
            self.ml_temp.cleanup()
        self.temp.cleanup()

    def az(self, args):
        return azure([*args, "--subscription", self.account["id"]], self.env)

    def enable_ml(self):
        if not hasattr(self, "ml_temp"):
            self.ml_temp = tempfile.TemporaryDirectory(prefix="mlop-finish-ml-")
        target = Path(self.ml_temp.name) / "ml"
        if not target.exists():
            original = Path(os.environ.get("AZURE_EXTENSION_DIR", str(Path.home() / ".azure/cliextensions"))) / "ml"
            if not original.exists():
                raise ValueError("The ml CLI extension is missing. Use the environment from 12.")
            target.symlink_to(original, target_is_directory=True)

    def ml(self, args):
        self.enable_ml()
        env = dict(self.env, AZURE_EXTENSION_DIR=self.ml_temp.name)
        return azure(["ml", *args, "--resource-group", self.group, "--workspace-name", self.workspace,
                      "--subscription", self.account["id"]], env)

    def get(self, path, version):
        return self.az(["rest", "--method", "get", "--url", self.base + path + "?api-version=" + version])

    def put(self, path, version, body):
        file = Path(self.temp.name) / "request.json"
        file.write_text(json.dumps(body))
        return self.az(["rest", "--method", "put", "--url", self.base + path + "?api-version=" + version,
                        "--body", "@" + str(file)])

    def role(self, principal, scope, role):
        url = f"https://management.azure.com{scope}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&$filter=atScope()"
        page = self.az(["rest", "--method", "get", "--url", url])
        if page.get("nextLink"):
            raise ValueError("Role pagination needs review.")
        if has_role(page["value"], principal, scope, role):
            return
        name = str(uuid5(NAMESPACE_URL, scope.lower() + principal.lower() + role))
        try:
            self.az(["role", "assignment", "create", "--name", name, "--assignee-object-id", principal,
                     "--assignee-principal-type", "ServicePrincipal", "--role", role, "--scope", scope,
                     "--query", "{name:name}"])
        except RuntimeError as error:
            page = self.az(["rest", "--method", "get", "--url", url])
            if "RoleAssignmentExists" not in str(error) or not has_role(page["value"], principal, scope, role):
                raise
