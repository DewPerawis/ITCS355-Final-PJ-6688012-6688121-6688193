# Local review without Azure

Use the companion submission ZIP for the shortest review path. It includes the exact public CSV and canonical model used by the saved evidence. It needs no Azure credentials and does not start cloud resources.

## Environment

Use Python 3.13.11 on Linux or WSL. Existing project users can activate ~/.venvs/mlop-pj. In a new review environment, open the extracted MLOP-PJ folder and run:

```bash
python3 --version
python3 -m venv .venv-review
source .venv-review/bin/activate
python -m pip install -r requirements-service.lock.txt httpx==0.28.1
```

Check the first command before continuing: it must report Python 3.13.11. Use the pinned packages, not current unpinned releases. No cloud packages are needed for local API checks.

## Check the supplied data and model

```bash
python -c 'import hashlib,json,pathlib; r=pathlib.Path("."); s=json.loads((r/"reports/data-source.json").read_text()); m=json.loads((r/"reports/bundle-manifest.json").read_text()); assert hashlib.sha256((r/s["raw_file"]).read_bytes()).hexdigest()==s["sha256"]; assert hashlib.sha256((r/m["artifact"]).read_bytes()).hexdigest()==m["artifact_sha256"]; print("Pinned data and model hashes match")'
python scripts/portability_audit.py
python -m unittest tests.test_contract_ci tests.test_api tests.test_runtime
```

The API tests check valid predictions, invalid requests (422), batch size, uncertain outputs, and semantic failure detection. They use an in-process API; no remote endpoint or paid request is involved. Model readiness checks verify the hash, package versions and golden profiles. Only load the supplied model after checking its hash; joblib is a Python serialization format.

## Run the API

```bash
python -m uvicorn service.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs. GET /ready should return 200. Use profiles from reports/golden-profiles.json for POST /predict. Inputs contain exactly 24 named numeric fields in [0,5], with 1-100 profiles per request. Stop the server with Ctrl+C.

The presentation notebook also supports MODE = "local". Select local mode in cell A before running setup A/B, then C-F. Its earlier cloud default is historical; the endpoint has been retired. Use J to stop its local server. Preserve the original saved notebook outputs when inspecting them.

## Reproduce training separately

Make another extracted copy first. The commands below run the study and overwrite that copy's generated reports and model outputs. They do not deploy to Azure.

```bash
python scripts/reproduce.py all
python -m unittest tests.test_api tests.test_runtime
```

This re-runs model selection and fitting. A new selection report includes timing values, so its derived model version and serialized bytes can differ from the historical canonical bundle. Do not overwrite the submitted evidence and call that the original cloud deployment. The current review did not run the full study again.

## Repository-only checkout

Git does not include raw data or binary model artifacts. Prefer the accompanying ZIP for the exact artifact. Alternatively download the UCI archive at source_url in reports/data-source.json, place google_review_ratings.csv in data/raw/, and verify its saved SHA-256. Then reproduce training in a separate copy as above. The private DVC remote and cloud registry are unavailable after verified cleanup.

See DATA_LICENSE.md for dataset attribution. See reports/submission-validation.json for the review actually performed; the commands above also describe steps a new reviewer can run.
