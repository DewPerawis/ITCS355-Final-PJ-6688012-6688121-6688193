import json
import logging
import os
import time
import threading
import uuid
import math
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt
from threadpoolctl import ThreadpoolController

from service.runtime import load_checked_bundle
from src.bundle import predict_profiles

logger = logging.getLogger("mlop_api")


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profiles: list[dict[str, StrictFloat | StrictInt]] = Field(min_length=1, max_length=100)


def create_app(root=None):
    root = Path(root or os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parents[1]))

    @asynccontextmanager
    async def lifespan(app):
        app.state.bundle = None
        app.state.manifest = None
        app.state.thread_controller = None
        app.state.predict_lock = threading.Lock()
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)
        logger.propagate = False
        try:
            manifest_path = root / "reports/bundle-manifest.json"
            manifest = json.loads(manifest_path.read_text())
            bundle, manifest = load_checked_bundle(
                root / manifest["artifact"], manifest_path, root / "reports/golden-profiles.json")
            app.state.golden = json.loads((root / "reports/golden-profiles.json").read_text())
            if os.environ.get("MLOP_FAILURE_MODE") == "wrong_mapping":
                if os.environ.get("DEPLOYMENT_STAGE") != "staging":
                    raise ValueError("Failure injection is allowed only in staging.")
                mapping = dict(bundle["mapping"])
                mapping[0], mapping[1] = mapping[1], mapping[0]
                bundle["mapping"] = mapping
            app.state.thread_controller = ThreadpoolController()
            app.state.bundle, app.state.manifest = bundle, manifest
        except Exception:
            logger.exception("Model load failed.")
        yield

    app = FastAPI(title="Travel Style API", lifespan=lifespan)

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        logger.info(json.dumps({"request_id": request.state.request_id, "path": request.url.path,
                               "status": response.status_code,
                               "duration_ms": (time.perf_counter() - started) * 1000,
                               "model_version": (app.state.manifest or {}).get("model_version")}))
        return response

    @app.get("/health")
    def health():
        return {"status": "alive"}

    @app.get("/ready")
    def ready():
        if app.state.bundle is None:
            raise HTTPException(status_code=503, detail="Model is not ready.")
        return {"status": "ready", "model_version": app.state.bundle["version"],
                "mapping_status": app.state.bundle["mapping_status"]}

    @app.post("/predict")
    def predict(body: PredictionRequest, request: Request):
        if app.state.bundle is None:
            raise HTTPException(status_code=503, detail="Model is not ready.")
        try:
            # The thread limit used by sklearn is shared within the process.
            with app.state.predict_lock:
                rows = predict_profiles(app.state.bundle, pd.DataFrame(body.profiles),
                                        thread_controller=app.state.thread_controller)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        for row in rows:
            row["status"] = "uncertain" if row["uncertain"] else "ok"
            if row["uncertain"]:
                row["segment"] = None
        logger.info(json.dumps({"event": "prediction_batch", "count": len(rows),
                               "uncertain_count": sum(row["uncertain"] for row in rows),
                               "model_version": app.state.bundle["version"]}))
        return {"request_id": request.state.request_id, "model_version": app.state.bundle["version"],
                "mapping_status": app.state.bundle["mapping_status"], "predictions": rows}

    @app.get("/canary")
    def canary():
        if app.state.bundle is None:
            raise HTTPException(status_code=503, detail="Model is not ready.")
        fixture = app.state.golden
        with app.state.predict_lock:
            actual = predict_profiles(app.state.bundle, pd.DataFrame(fixture["profiles"]),
                                      thread_controller=app.state.thread_controller)
        passed = all(row["cluster_id"] == expected["cluster_id"]
                     and row["segment"] == expected["segment"]
                     and row["uncertain"] == expected["uncertain"]
                     and math.isclose(row["distance"], expected["distance"], rel_tol=1e-9, abs_tol=1e-9)
                     for row, expected in zip(actual, fixture["expected"]))
        if not passed:
            logger.error(json.dumps({"event": "semantic_canary_failed", "model_version": app.state.bundle["version"]}))
            raise HTTPException(status_code=503, detail="Semantic canary failed.")
        return {"passed": True, "model_version": app.state.bundle["version"]}

    return app


app = create_app()
