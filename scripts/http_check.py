import json
import math
import ssl
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener

import numpy as np

TLS_CONTEXT = ssl.create_default_context()
CLIENT = threading.local()


def http_call(url, path, payload=None, timeout=10):
    # Reuse client setup. Keep certificate checks enabled for HTTPS.
    if not hasattr(CLIENT, "opener"):
        CLIENT.opener = build_opener(ProxyHandler({}), HTTPSHandler(context=TLS_CONTEXT))
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(url + path, data=data, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        response = CLIENT.opener.open(request, timeout=timeout)
    except HTTPError as error:
        response = error
    with response:
        status, body = response.status, json.loads(response.read())
    return status, body, (time.perf_counter() - started) * 1000


def check_predictions(body, expected, version):
    if body.get("model_version") != version or len(body.get("predictions", [])) != len(expected):
        raise ValueError("Wrong model version or prediction count.")
    for actual, reference in zip(body["predictions"], expected):
        segment = None if reference["uncertain"] else reference["segment"]
        status = "uncertain" if reference["uncertain"] else "ok"
        if (actual.get("cluster_id") != reference["cluster_id"]
                or actual.get("model_version") != version
                or actual.get("uncertain") != reference["uncertain"]
                or actual.get("segment") != segment or actual.get("status") != status
                or not math.isclose(actual.get("distance", math.inf), reference["distance"],
                                    rel_tol=1e-9, abs_tol=1e-9)):
            raise ValueError("Prediction differs from the saved golden result.")


def smoke(url, fixture):
    health, health_body, _ = http_call(url, "/health")
    ready, ready_body, _ = http_call(url, "/ready")
    valid, prediction, _ = http_call(url, "/predict", {"profiles": fixture["profiles"]})
    invalid, _, _ = http_call(url, "/predict", {"profiles": [{"Category 1": 2}]})
    batch, batch_body, _ = http_call(url, "/predict", {"profiles": [fixture["profiles"][0]] * 100})
    codes = [health, ready, valid, invalid, batch]
    if codes != [200, 200, 200, 422, 200] or health_body.get("status") != "alive":
        raise ValueError(f"HTTP smoke check failed: {codes}")
    if ready_body.get("model_version") != fixture["model_version"]:
        raise ValueError("Readiness reports another model.")
    check_predictions(prediction, fixture["expected"], fixture["model_version"])
    check_predictions(batch_body, [fixture["expected"][0]] * 100, fixture["model_version"])
    return {"passed": True, "transport": "real HTTP", "url": url, "status_codes": codes,
            "model_version": fixture["model_version"], "golden_predictions_match": True,
            "batch_100_passed": True}


def load_check(url, fixture, requests=200, concurrency=10):
    if requests < concurrency or concurrency < 1:
        raise ValueError("Use requests >= concurrency >= 1.")
    # Warm requests are checked but excluded from latency statistics.
    for _ in range(10):
        status, body, _ = http_call(url, "/predict", {"profiles": [fixture["profiles"][0]]})
        if status != 200:
            raise ValueError("Warm-up request failed.")
        check_predictions(body, [fixture["expected"][0]], fixture["model_version"])

    def send(index):
        row = index % len(fixture["profiles"])
        started = time.perf_counter()
        try:
            status, body, elapsed = http_call(url, "/predict", {"profiles": [fixture["profiles"][row]]})
            if status != 200:
                raise ValueError(f"HTTP {status}")
            check_predictions(body, [fixture["expected"][row]], fixture["model_version"])
            return {"ok": True, "latency_ms": elapsed}
        except Exception as error:
            return {"ok": False, "latency_ms": (time.perf_counter() - started) * 1000,
                    "error": f"{type(error).__name__}: {error}"}

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        outcomes = list(pool.map(send, range(requests)))
    elapsed = time.perf_counter() - started
    latencies = [row["latency_ms"] for row in outcomes if row["ok"]]
    failures = requests - len(latencies)
    p95 = float(np.percentile(latencies, 95)) if latencies else None
    return {"scope": "local real HTTP; not Azure performance", "model_version": fixture["model_version"],
            "requests": requests, "concurrency": concurrency, "batch_size": 1,
            "warmup_requests": 10, "errors": failures, "error_rate": failures / requests,
            "duration_seconds": elapsed, "successful_requests_per_second": len(latencies) / elapsed,
            "mean_ms": float(np.mean(latencies)) if latencies else None, "p95_ms": p95,
            "latency_scope": "successful requests; client HTTP time including response parsing",
            "client_setup": "shared verified TLS context; per-thread opener reused; setup outside request timer",
            "workload": "cycle five saved golden profiles; closed-loop clients",
            "target_p95_ms": 300, "target_met": failures == 0 and p95 is not None and p95 < 300,
            "outcomes": outcomes}
