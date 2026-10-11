import json
import logging
import os
import time
import threading
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt

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
        app.state.predict_lock = threading.Lock()
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)
        logger.propagate = False
        try:
            manifest_path = root / "reports/bundle-manifest.json"
            manifest = json.loads(manifest_path.read_text())
            app.state.bundle, app.state.manifest = load_checked_bundle(
                root / manifest["artifact"], manifest_path, root / "reports/golden-profiles.json")
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
                rows = predict_profiles(app.state.bundle, pd.DataFrame(body.profiles))
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        for row in rows:
            row["status"] = "uncertain" if row["uncertain"] else "ok"
            if row["uncertain"]:
                row["segment"] = None
        return {"request_id": request.state.request_id, "model_version": app.state.bundle["version"],
                "mapping_status": app.state.bundle["mapping_status"], "predictions": rows}

    return app


app = create_app()
