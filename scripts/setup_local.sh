#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
python_bin="$HOME/.venvs/mlop-pj/bin/python"
if [[ ! -x "$python_bin" ]]; then
    echo 'Run setup_wsl.sh first.'
    exit 1
fi
"$python_bin" -m pip install -c requirements-notebook.lock.txt -r requirements-local.txt
"$python_bin" -m pip check
"$python_bin" - <<'PY'
import json
import platform
from importlib import metadata
from pathlib import Path

import dvc
import fastapi
import httpx
import mlflow
import uvicorn

selected = json.loads(Path('reports/selection.json').read_text())
assert platform.python_version() == selected['python'], 'Python changed.'
for name, expected in selected['packages'].items():
    assert metadata.version(name) == expected, f'Training package changed: {name}'
print('Tracking and API imports passed. Training package versions are unchanged.')
for name in ['mlflow', 'dvc', 'fastapi', 'uvicorn', 'httpx']:
    print(name, metadata.version(name))
PY
"$python_bin" -m pip freeze > requirements-local.lock.txt
echo 'Ready. Restart the notebook kernel, then run 05 and 06.'
