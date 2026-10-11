#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
env_dir="$HOME/.venvs/mlop-pj"
cd "$project_dir"

if [[ -e "$env_dir" && ! -f "$env_dir/pyvenv.cfg" ]]; then
    echo "The environment path exists but is not a venv: $env_dir"
    exit 1
fi
if [[ ! -f "$env_dir/pyvenv.cfg" ]]; then
    if ! python3 -c 'import ensurepip' 2>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-venv
    fi
    python3 -m venv "$env_dir"
fi
python_bin="$env_dir/bin/python"
"$python_bin" -m pip install --only-binary=:all: -r requirements-notebook.txt
"$python_bin" -m pip check
"$python_bin" - <<'PY'
import sys
import numpy as np
import pandas as pd
import matplotlib
import sklearn
from sklearn.cluster import KMeans

sample = pd.DataFrame([[0, 0], [0, 1], [4, 4], [4, 5]])
labels = KMeans(n_clusters=2, n_init=10, random_state=42).fit_predict(sample)
assert len(np.unique(labels)) == 2
print("Imports and small K-Means check passed.")
print("Python:", sys.executable)
for package in [np, pd, sklearn, matplotlib]:
    print(package.__name__, package.__version__)
PY
"$python_bin" -m ipykernel install --user --name mlop-pj --display-name 'MLOP-PJ (WSL)'
"$python_bin" -m pip freeze > requirements-notebook.lock.txt
echo 'Ready. Open VS Code in WSL and select MLOP-PJ (WSL).'
