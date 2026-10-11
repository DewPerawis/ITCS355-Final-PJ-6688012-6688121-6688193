"""Small display and API helpers for the presentation notebook."""

import atexit
import html
import json
import math
import os
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from IPython.display import HTML, display

from scripts.http_check import check_predictions, http_call


CATEGORIES = [
    "Churches", "Resorts", "Beaches", "Parks", "Theatres", "Museums",
    "Malls", "Zoos", "Restaurants", "Pubs / bars", "Local services",
    "Burger / pizza shops", "Hotels / lodgings", "Juice bars", "Art galleries",
    "Dance clubs", "Swimming pools", "Gyms", "Bakeries", "Beauty / spas",
    "Cafes", "View points", "Monuments", "Gardens",
]


def panel(title, message, rows=(), ok=None):
    color = "#21618c" if ok is None else "#237347" if ok else "#b33434"
    cells = "".join(
        f'<tr><td style="padding:6px 16px 6px 0">{html.escape(str(key))}</td>'
        f'<td style="padding:6px 0"><b>{html.escape(str(value))}</b></td></tr>'
        for key, value in rows
    )
    display(HTML(
        f'<div style="background:#fff;color:#17212b;border:2px solid {color};'
        'border-radius:12px;padding:18px;margin:10px 0;font:18px Arial;max-width:900px">'
        f'<h3 style="color:{color};margin:0 0 12px">{html.escape(title)}</h3>'
        f'<p>{html.escape(message)}</p><table>{cells}</table></div>'
    ))


class Demo:
    def __init__(self, root, mode="cloud"):
        if mode not in {"cloud", "local"}:
            raise ValueError('Choose MODE = "cloud" or "local".')
        self.root = Path(root)
        self.mode = mode
        self.fixture = self.read("reports/golden-profiles.json")
        self.manifest = self.read("reports/bundle-manifest.json")
        self.deploy = self.read("reports/ci-deploy-result.json")
        if self.fixture["artifact_sha256"] != self.manifest["artifact_sha256"]:
            raise ValueError("The fixture and manifest belong to different bundles.")
        self.version = self.fixture["model_version"]
        self.process = None
        self.log = None
        self.prepared = False
        self.url = self.deploy["url"] if mode == "cloud" else None
        if mode == "cloud":
            address = urlsplit(self.url)
            if address.scheme != "https" or not (address.hostname or "").endswith(".azurecontainerapps.io"):
                raise ValueError("Use the recorded Azure HTTPS endpoint.")
        atexit.register(self.close)

    def read(self, name):
        return json.loads((self.root / name).read_text(encoding="utf-8"))

    @property
    def label(self):
        return "LIVE AZURE API" if self.mode == "cloud" else "LIVE LOCAL API — NOT AZURE"

    def start_local(self):
        artifact = self.root / self.manifest["artifact"]
        if not artifact.is_file():
            raise RuntimeError("The local bundle is missing. Cloud mode does not need this file.")
        # Use a free loopback port and stop only the process started by this demo.
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        directory = self.root / "tmp"
        directory.mkdir(exist_ok=True)
        self.log = tempfile.NamedTemporaryFile(mode="w", prefix="demo-api-", suffix=".log", dir=directory, delete=False)
        env = os.environ.copy()
        env.pop("MLOP_FAILURE_MODE", None)
        env["DEPLOYMENT_STAGE"] = "local-demo"
        env["PROJECT_ROOT"] = str(self.root)
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "service.app:app", "--host", "127.0.0.1",
             "--port", str(port), "--log-level", "warning"],
            cwd=self.root, env=env, stdout=self.log, stderr=subprocess.STDOUT,
        )
        self.url = f"http://127.0.0.1:{port}"

    def prepare(self):
        self.close()
        if self.mode == "local":
            self.start_local()
        print(f"Preparing {self.label}. The first cloud request may need a cold start.")
        last_error = ""
        ready = False
        deadline = time.monotonic() + 150
        try:
            while time.monotonic() < deadline:
                if self.process is not None and self.process.poll() is not None:
                    raise RuntimeError("Local API stopped. Check its log and runtime packages.")
                try:
                    code, body, _ = http_call(self.url, "/ready", timeout=60)
                    ready = code == 200 and body.get("model_version") == self.version
                    if ready:
                        break
                    last_error = f"Readiness returned HTTP {code} or a different model."
                except (OSError, ValueError) as error:
                    last_error = str(error)
                time.sleep(2)
            if not ready:
                raise RuntimeError(last_error or "The API did not become ready.")
            code, body, _ = http_call(self.url, "/health", timeout=60)
            if code != 200 or body.get("status") != "alive":
                raise ValueError("Health check failed.")
            code, body, _ = http_call(self.url, "/canary", timeout=60)
            if code != 200 or not body.get("passed") or body.get("model_version") != self.version:
                raise ValueError("The semantic canary did not pass.")
            code, body, _ = http_call(self.url, "/predict", {"profiles": self.fixture["profiles"]}, timeout=60)
            if code != 200:
                raise ValueError("Golden profiles were rejected.")
            check_predictions(body, self.fixture["expected"], self.version)
            code, _, _ = http_call(self.url, "/predict", {"profiles": [{"Category 1": 2}]}, timeout=60)
            if code != 422:
                raise ValueError("The missing-field check did not return 422.")
            code, body, _ = http_call(self.url, "/predict", {"profiles": [self.profile()] * 100}, timeout=60)
            if code != 200:
                raise ValueError("The batch check failed.")
            check_predictions(body, [self.fixture["expected"][0]] * 100, self.version)
        except Exception as error:
            self.prepared = False
            panel("PREPARATION STOPPED", str(error), [("Mode", self.label)], ok=False)
            if self.log is not None:
                print("Local API log:", self.log.name)
            self.close()
            raise RuntimeError("Fix preparation before presenting. Do not claim a live success.") from error
        self.prepared = True
        panel("READY FOR DEMO", "Readiness, canary, golden predictions, invalid input and batch checks passed.",
              [("Mode", self.label), ("Model", self.version)], ok=True)

    def profile(self, case=0):
        if type(case) is not int or not 0 <= case < len(self.fixture["profiles"]):
            raise ValueError("Choose CASE from 0 to 4.")
        return self.fixture["profiles"][case].copy()

    def show_input(self, profile):
        rows = []
        for number, category in enumerate(CATEGORIES, 1):
            value = float(profile[f"Category {number}"])
            if not math.isfinite(value) or not 0 <= value <= 5:
                raise ValueError("Display ratings must be finite and between 0 and 5.")
            rows.append((category, value, number))
        bars = "".join(
            '<div style="display:grid;grid-template-columns:150px 1fr 50px;gap:12px;align-items:center;margin:10px 0">'
            f'<span>{html.escape(category)}</span><div style="background:#e8edf0;height:18px">'
            f'<div style="background:#21618c;width:{value / 5 * 100:.1f}%;height:18px"></div></div>'
            f'<b>{value:.2f}</b></div>' for category, value, _ in rows[:6]
        )
        details = "".join(f'<li>Category {number}: {html.escape(category)} = {value:.2f}</li>'
                          for category, value, number in rows)
        display(HTML(
            '<div style="background:#fff;color:#17212b;padding:20px;border:1px solid #abc;border-radius:12px;'
            'max-width:900px;font:18px Arial"><h3>INPUT: one example profile</h3>'
            '<p>24 ratings are sent. Six are shown below. Zero meaning is unknown.</p>'
            f'{bars}<details><summary>Show all 24 ratings</summary><ul>{details}</ul></details></div>'
        ))

    def request(self, path, payload=None):
        if not self.prepared:
            raise RuntimeError("Run preparation first.")
        try:
            return http_call(self.url, path, payload, timeout=60)
        except (OSError, ValueError) as error:
            panel("LIVE REQUEST FAILED", str(error), [("Mode", self.label)], ok=False)
            raise RuntimeError("The live request failed. Saved evidence is not a live result.") from error

    def predict(self, profile, case=None):
        code, body, _ = self.request("/predict", {"profiles": [profile]})
        if code != 200:
            panel("INPUT REJECTED", str(body.get("detail", body)), [("HTTP", code), ("Mode", self.label)])
            return code, body
        if case is not None:
            check_predictions(body, [self.fixture["expected"][case]], self.version)
        if body.get("model_version") != self.version or len(body.get("predictions", [])) != 1:
            raise ValueError("Unexpected prediction version or count.")
        row = body["predictions"][0]
        message = "This profile is far from its group. No segment name is returned." if row["uncertain"] else "The profile was assigned a provisional group."
        panel("PREDICTION", message,
              [("Mode", self.label), ("Segment", row["segment"] or "No label (uncertain)"),
               ("Uncertain", "Yes" if row["uncertain"] else "No"),
               ("Distance", f'{row["distance"]:.4f} — not a probability'),
               ("Model", body["model_version"])], ok=True)
        return code, body

    def invalid(self):
        code, body, _ = self.request("/predict", {"profiles": [{"Category 1": 2}]})
        if code != 422:
            raise ValueError("Expected HTTP 422 for missing fields.")
        panel("INVALID INPUT: SAFELY REJECTED", "Only one rating was sent; the API needs all 24.",
              [("Mode", self.label), ("HTTP", code), ("Reason", body.get("detail", body))], ok=True)
        return code

    def batch(self):
        code, body, _ = self.request("/predict", {"profiles": [self.profile()] * 100})
        if code != 200:
            raise ValueError("Batch 100 was rejected.")
        check_predictions(body, [self.fixture["expected"][0]] * 100, self.version)
        panel("BATCH: 100 PREDICTIONS", "One example is repeated 100 times to check the batch limit.",
              [("Mode", self.label), ("Profiles sent", 100), ("Predictions checked", 100), ("HTTP", code)], ok=True)
        return code

    def show_ci(self):
        saved = self.read("reports/ci-runs.json")
        good = next(r for r in saved["runs"] if r["conclusion"] == "success")
        bad = next(r for r in saved["runs"] if r["conclusion"] == "failure")
        if good["head_sha"] != bad["head_sha"] or not saved.get("intentional_test_failure_verified"):
            raise ValueError("Saved CI evidence is incomplete.")
        for run, expected in [(good, {"tests": "success", "deploy": "success"}),
                              (bad, {"tests": "failure", "deploy": "skipped"})]:
            if {job["name"]: job["conclusion"] for job in run["jobs"]} != expected:
                raise ValueError("Saved CI jobs do not match the claimed gate.")
        panel("SAVED CI EVIDENCE", "These are completed GitHub runs, not newly started workflows.",
              [("Normal run", "Tests passed; deploy passed"),
               ("Deliberate test failure", "Tests failed; deploy skipped"),
               ("Tested source", good["head_sha"][:7])], ok=True)
        for label, run in [("Normal run", good), ("Deliberate failure", bad)]:
            display(HTML(f'<p><a href="{html.escape(run["html_url"], quote=True)}" target="_blank">{label}: open GitHub Actions</a></p>'))

    def show_incident(self):
        failure = self.read("reports/finish-failure.json")
        alert = self.read("reports/finish-alert.json")
        if not failure.get("failure_detected") or not failure.get("recovered") or not alert.get("alert_fired"):
            raise ValueError("Saved failure, recovery or alert evidence is incomplete.")
        elapsed = (datetime.fromisoformat(failure["recovered_at"]) - datetime.fromisoformat(failure["detected_at"])).total_seconds()
        panel("SAVED STAGING INCIDENT", "A wrong segment mapping was detected and restored. The first recovery attempt failed.",
              [("Canary during fault", failure["observed_canary_status"]),
               ("Actual alert event", "Fired"), ("Canary after recovery", failure["recovery_canary_status"]),
               ("Detection to recovery", f"{int(elapsed) // 60} min {elapsed % 60:.1f} sec"),
               ("Recovery", "Config restore and restart; not automatic alert rollback")], ok=True)

    def close(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.log is not None:
            self.log.close()
            self.log = None
        self.prepared = False
