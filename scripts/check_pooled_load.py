import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import httpx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.http_check import check_predictions


def main():
    fixture = json.loads((ROOT / 'reports/golden-profiles.json').read_text())
    url = json.loads((ROOT / 'reports/ci-deploy-result.json').read_text())['url']
    with httpx.Client(timeout=60, trust_env=False,
                      limits=httpx.Limits(max_connections=10, max_keepalive_connections=10)) as client:
        def send(index):
            row = index % len(fixture['profiles'])
            started = time.perf_counter()
            try:
                response = client.post(url + '/predict', json={'profiles': [fixture['profiles'][row]]})
                body = response.json()
                elapsed = (time.perf_counter() - started) * 1000
                response.raise_for_status()
                check_predictions(body, [fixture['expected'][row]], fixture['model_version'])
                return {'ok': True, 'latency_ms': elapsed}
            except Exception as error:
                return {'ok': False, 'error': type(error).__name__,
                        'latency_ms': (time.perf_counter() - started) * 1000}

        with ThreadPoolExecutor(max_workers=10) as pool:
            warmup = list(pool.map(send, range(10)))
            if not all(row['ok'] for row in warmup):
                raise RuntimeError('Warmup failed. Check the API before measuring.')
            started = time.perf_counter()
            rows = list(pool.map(send, range(200)))
            duration = time.perf_counter() - started
    latencies = [row['latency_ms'] for row in rows if row['ok']]
    errors = sum(not row['ok'] for row in rows)
    p95 = float(np.percentile(latencies, 95)) if latencies else None
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Azure HTTPS from WSL using a verified HTTPX connection pool',
              'requests': 200, 'concurrency': 10, 'batch_size': 1, 'warmup_requests': 10,
              'warmup': 'Ten concurrent checked requests, excluded from results',
              'client': 'httpx ' + httpx.__version__, 'persistent_connections': True,
              'latency_scope': 'Client request and JSON parsing; includes network; golden checks follow the timer',
              'model_version': fixture['model_version'], 'errors': errors, 'p95_ms': p95,
              'mean_ms': float(np.mean(latencies)) if latencies else None, 'duration_seconds': duration,
              'target_p95_ms': 300, 'target_met': errors == 0 and p95 is not None and p95 < 300,
              'limits': 'Different client and warm-up method from azure-load.json. Report both; do not compare as a server-only optimisation.',
              'outcomes': rows}
    (ROOT / 'reports/pooled-load.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'outcomes'}, indent=2))


if __name__ == '__main__':
    main()
