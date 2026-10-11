# Remaining work

Status: 11 October 2026, after the saved 17 upload verification. The local model, API, Docker image, and Azure platform are ready. The online Azure API and final capstone evidence are still pending.

Use five milestones. Reuse notebooks for grouped script runs; do not add one notebook per small check. Notebook 17 is complete. Use one notebook per main part: 18 live API, 19 training/registry, 20 monitoring/recovery, 21 CI/CD, and 22 delivery.

| Milestone | Work | Done when |
|---|---|---|
| 1. Data, training, registry | Blob upload complete; configure DVC Azure remote, prove fresh pull, connect reproducible training to Azure ML, register the bundle with data/code/run lineage | Verified remote round trip, successful training run and registry version |
| 2. Live API | Push the tested immutable image to ACR, deploy Container Apps, test valid/invalid/batch requests, measure warm and cold latency | Reachable endpoint and saved smoke/load results |
| 3. CI/CD | Add test/build/deploy workflow and scoped identity; run a valid change and a deliberately bad change | Successful deployment and evidence that failed tests block deployment |
| 4. Monitoring and recovery | Run the controlled input-drift experiment; connect service telemetry, dashboard and one alert; trigger the planned staging failure, observe it, roll back and add a regression check | Dashboard, delivered alert, failure/recovery timestamps and passing regression check |
| 5. Delivery evidence | One-page model card, cost per 1,000 predictions, portability audit, reproducibility README and demo instructions; cleanup after evidence is saved and cleanup is authorized | Required files and checks complete, plus verified cleanup at the agreed time |

Each milestone can need several commands and cloud waits. No verified completion-time estimate is available. Cloud services already exist and may incur charges. The cleanup tag is a reminder, not automatic deletion.

Next: run Notebook 18 setup, package setup, and assets/deploy. The source is prepared; cloud and GitHub runs still need evidence. Do not rerun 17 for the earlier import fix.
