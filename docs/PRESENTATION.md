# Presentation

Open `output/presentation/MLOP-PJ_Presentation.pptx`. It has 15 slides, short speaker notes, and an 8-minute plan. Keep 5 more minutes for questions. The PDF is in `output/pdf/MLOP-PJ_Presentation.pdf`.

| Slides | Topic | Time |
|---|---|---|
| 1-2 | Team and problem | 60 seconds |
| 3-5 | Architecture, data, registry | 90 seconds |
| 6 | Live API demo | 90 seconds |
| 7-9 | CI, latency, monitoring | 85 seconds |
| 10-12 | Failure, drift, cost | 95 seconds |
| 13-15 | Next week, references, questions | 60 seconds |

## Live demo

Use the project WSL kernel in Notebook 22. Add one temporary cell and run this before presenting. It makes a few API requests; it does not retrain or change cloud configuration.

```python
import json
import sys
from pathlib import Path

ROOT = next(p for p in (Path.cwd(), *Path.cwd().parents)
            if (p / "reports/golden-profiles.json").is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.http_check import http_call, smoke

fixture = json.loads((ROOT / "reports/golden-profiles.json").read_text())
url = json.loads((ROOT / "reports/ci-deploy-result.json").read_text())["url"]
print("Ready:", http_call(url, "/ready", timeout=60)[:2])
print("Checks:", smoke(url, fixture))
print("Prediction:", http_call(url, "/predict", {"profiles": [fixture["profiles"][0]]})[:2])
print("Missing fields:", http_call(url, "/predict", {"profiles": [{"Category 1": 2}]})[:2])
```

Show the segment, version, and uncertainty flag. Then show the 422 validation error and the successful batch check. Open the two Actions links on slide 7. Show the saved incident on slide 10; do not inject another fault during a short talk.

## Evidence and limits

The slides use saved project reports and a real API smoke check. Graphs are drawn from those reports; they are not Portal screenshots. Sources and figure paths are in `output/presentation/slide_sources.json`.

- CI evidence covers source commit `1e0bd12`. Later local code still needs final CI checks.
- Warm cloud p95 missed 300 ms. Cold start is one 3.82-second request, not a percentile.
- Input drift is an offline controlled shift. Logged application latency and client HTTPS latency are different measures.
- Keep the planning estimate separate from the provisional reported cost. The reported row may not include all usage yet.
- Save real dashboard and alert screenshots before cleanup. The reminder is 13 October 2026, 21:15 Bangkok; it does not delete resources.

The deck keeps the supplied template's backgrounds, decoration, fonts, and Mahidol logo. Old research text, other institutions, speaker notes, and embedded objects were removed from the new file. The original `example.pptx` was kept unchanged.
