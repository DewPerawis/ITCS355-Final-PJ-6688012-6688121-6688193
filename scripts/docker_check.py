import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from http_check import http_call, load_check, smoke

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUTPUT = REPORTS


def command(args, timeout=60, log=None):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if log:
        (OUTPUT / log).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Command failed: {args[0]}")
    return result.stdout.strip()


def save(name, report):
    (OUTPUT / name).write_text(json.dumps(report, indent=2) + "\n")


def main():
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--reuse-image", action="store_true")
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()
    if args.requests < args.concurrency or args.concurrency < 1:
        parser.error("Use requests >= concurrency >= 1.")
    OUTPUT = (ROOT / args.report_dir).resolve()
    if not OUTPUT.is_relative_to(REPORTS.resolve()):
        parser.error("Keep the report folder inside reports/.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((REPORTS / "bundle-manifest.json").read_text())
    fixture = json.loads((REPORTS / "golden-profiles.json").read_text())
    version = manifest["model_version"]
    if not re.fullmatch(r"[a-f0-9]{12}", version):
        raise ValueError("Unexpected bundle version.")
    artifact = ROOT / "models/artifacts" / version / "bundle.joblib"
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != manifest["artifact_sha256"]:
        raise ValueError("Bundle hash differs. Stop before building.")
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for folder in ["src", "service"] for p in sorted((ROOT / folder).glob("*.py"))}
    lock_hash = hashlib.sha256((ROOT / "requirements-service.lock.txt").read_bytes()).hexdigest()
    if args.reuse_image:
        previous = json.loads((REPORTS / "docker-image.json").read_text())
        if (previous["model_version"] != version or previous["artifact_sha256"] != manifest["artifact_sha256"]
                or previous["source_sha256"] != source_hashes or previous["service_lock_sha256"] != lock_hash):
            raise ValueError("The saved image belongs to different code, packages, or model. Rebuild first.")
        image = json.loads(command(["docker", "image", "inspect", previous["image_id"]]))[0]
        base_ref, image_tag = previous["base_image"], previous["image_tag"]
        print("Reusing the exact image from 08. No download or rebuild.", flush=True)
    else:
        base_tag = "python:" + ".".join(manifest["python"].split(".")[:2]) + "-slim"
        print(f"Pulling {base_tag} and building the API image. This may take a few minutes.", flush=True)
        command(["docker", "pull", base_tag], timeout=600, log="docker-pull.txt")
        base = json.loads(command(["docker", "image", "inspect", base_tag]))[0]
        base_ref = base["RepoDigests"][0]
        image_tag = "mlop-pj-api:" + version
        command(["docker", "build", "--build-arg", f"PYTHON_IMAGE={base_ref}",
                 "--build-arg", f"MODEL_VERSION={version}", "-t", image_tag, "."],
                timeout=900, log="docker-build.txt")
        image = json.loads(command(["docker", "image", "inspect", image_tag]))[0]
    image_report = {"created_at": datetime.now(timezone.utc).isoformat(), "base_image": base_ref,
                    "image_tag": image_tag, "image_id": image["Id"], "size_bytes": image["Size"],
                    "architecture": image["Architecture"], "os": image["Os"],
                    "model_version": version, "artifact_sha256": manifest["artifact_sha256"],
                    "source_sha256": source_hashes, "service_lock_sha256": lock_hash,
                    "reused_image": args.reuse_image,
                    "container_limits": {"cpus": 1, "memory_mb": 512}, "cloud_uploaded": False}
    save("docker-image.json", image_report)
    container = None
    started = time.perf_counter()
    try:
        container = command(["docker", "run", "-d", "--rm", "--read-only", "--cap-drop=ALL",
                             "--security-opt=no-new-privileges", "--memory=512m", "--cpus=1",
                             "--pids-limit=128", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
                             "-p", "127.0.0.1::8000", image["Id"]])
        info = json.loads(command(["docker", "inspect", container]))[0]
        port = info["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"]
        url = f"http://127.0.0.1:{port}"
        deadline = time.perf_counter() + 60
        while time.perf_counter() < deadline:
            try:
                status, _, _ = http_call(url, "/ready")
                if status == 200:
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError("Container readiness did not pass within 60 seconds. Read docker-api.log.")
        startup_ms = (time.perf_counter() - started) * 1000
        smoke_report = smoke(url, fixture)
        smoke_report.update({"image_id": image["Id"], "startup_to_ready_ms": startup_ms,
                             "startup_scope": "local Docker run to ready, including polling; not Azure cold start"})
        save("docker-smoke.json", smoke_report)
        print("HTTP smoke passed. Measuring 200 requests at concurrency 10 by default.", flush=True)
        load_report = load_check(url, fixture, args.requests, args.concurrency)
        load_report.update({"image_id": image["Id"], "created_at": datetime.now(timezone.utc).isoformat(),
                            "checker_sha256": hashlib.sha256((ROOT / "scripts/http_check.py").read_bytes()).hexdigest()})
        save("local-load.json", load_report)
        print(json.dumps({key: value for key, value in load_report.items() if key != "outcomes"}, indent=2))
        if load_report["errors"]:
            raise RuntimeError("Load requests failed. Review local-load.json.")
    finally:
        if container:
            logs = subprocess.run(["docker", "logs", container], capture_output=True, text=True, timeout=30)
            (OUTPUT / "docker-api.log").write_text(logs.stdout + logs.stderr)
            command(["docker", "stop", container], timeout=40)
            print("The test container stopped. The local image and reports are kept.", flush=True)


if __name__ == "__main__":
    main()
