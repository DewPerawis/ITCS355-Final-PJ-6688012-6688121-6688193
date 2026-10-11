import os

from cloudlayer.finish_serve import app_body, wait_ready
from cloudlayer.session import ROOT, Session, read, write
from scripts.http_check import smoke


if __name__ == "__main__":
    with Session() as cloud:
        image = os.environ["IMAGE_URI"]
        if not image.startswith(cloud.host + "/travel-style@sha256:"):
            raise ValueError("Use an immutable image in the project registry.")
        current = cloud.get("Microsoft.App/containerApps/" + cloud.app, "2025-07-01")
        if (current.get("tags") or {}).get("project") != cloud.tags["project"]:
            raise ValueError("The endpoint has different ownership.")
        identities = list(current.get("identity", {}).get("userAssignedIdentities", {}))
        if len(identities) != 1:
            raise ValueError("Expected one existing app pull identity.")
        body = app_body(cloud, image, identities[0])
        cloud.put("Microsoft.App/containerApps/" + cloud.app, "2025-07-01", body)
        url, _, _ = wait_ready(cloud, cloud.app)
        result = smoke(url, read("reports/golden-profiles.json"))
        result.update(image_uri=image, git_sha=os.environ["GITHUB_SHA"],
                      github_run=os.environ["GITHUB_SERVER_URL"] + "/" + os.environ["GITHUB_REPOSITORY"] + "/actions/runs/" + os.environ["GITHUB_RUN_ID"])
        write("reports/ci-deploy-result.json", result)
