# Notebook 09 review

- The exact image from 08 passed HTTP smoke and all 200 load requests.
- Corrected client mean: 267.01 ms. Corrected p95: 496.01 ms. The 300 ms target still failed.
- API logs also showed about 492 ms p95. The remaining delay is not only client setup.
- A 20-call profile found repeated native-library discovery and duplicate preprocessing in the prediction path.
- Serving now reuses a thread controller loaded after the bundle and transforms each batch once. The prediction lock still protects process-wide thread limits.
- All 5,454 prepared profiles matched the old function exactly, including distances and uncertainty. All 15 existing tests passed after the change.
- A separate WSL 20-call check averaged 13.90 ms before and 3.87 ms after. This small check is not a Docker concurrency result.
- The model artifact, training settings, and data are unchanged. Original source files and user results are in `reports/history/09-initial/`.
- Notebook 10 builds the updated serving image and writes to `reports/serving-recheck/`. Its Docker p95 is not measured yet.
- The original selection records the older `src/bundle.py` hash. Its matching snapshot is preserved. The changed prediction path does not require rerunning 00-05 to serve this saved artifact. If training is rerun later, start with 03 to create new code provenance before 04; the source-hash guard remains enabled.

References: [threadpoolctl controller API](https://github.com/joblib/threadpoolctl), [Azure provider checks](https://learn.microsoft.com/en-us/cli/azure/provider), [VM usage checks](https://learn.microsoft.com/en-us/cli/azure/vm#az-vm-list-usage).
