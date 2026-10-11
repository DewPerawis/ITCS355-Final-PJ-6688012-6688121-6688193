import argparse
import json
import os
import tempfile
from datetime import datetime, timezone

from cloudlayer.platform_preview import azure, check_group, plan_for
from cloudlayer.session import read, write


def cleanup(confirm_group):
    with tempfile.TemporaryDirectory(prefix="mlop-cleanup-") as directory:
        env = dict(os.environ, AZURE_EXTENSION_DIR=directory)
        account = azure(["account", "show", "--query", "{id:id,state:state}"], env)
        plan = plan_for(account, read("configs/azure.json"))
        if confirm_group != plan["resource_group"]:
            raise ValueError("Enter the exact project resource group with --confirm-group.")
        def run(args):
            return azure([*args, "--subscription", account["id"]], env)
        report = {"checked_at": datetime.now(timezone.utc).isoformat(), "resource_group": confirm_group, "cleanup_verified": False}
        if run(["group", "exists", "--name", confirm_group]):
            group = run(["group", "show", "--name", confirm_group, "--query", "{location:location,tags:tags}"])
            check_group(group, plan)
            report["resources_before"] = run(["resource", "list", "--resource-group", confirm_group, "--query", "[].{name:name,type:type}"])
            run(["group", "delete", "--name", confirm_group, "--yes"])
        report["cleanup_verified"] = not run(["group", "exists", "--name", confirm_group])
        write("reports/cleanup.json", report)
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-group", required=True)
    print(json.dumps(cleanup(parser.parse_args().confirm_group), indent=2))
