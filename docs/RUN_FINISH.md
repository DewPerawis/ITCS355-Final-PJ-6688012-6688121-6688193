# Finish the project

**Historical operations guide.** The demo has finished, cloud cleanup is verified, and the deployment workflow is disabled. The steps below describe the original setup; do not rerun them for final review. Use [LOCAL_REVIEW.md](LOCAL_REVIEW.md) and [FINAL_SUBMISSION.md](FINAL_SUBMISSION.md).

Use `notebooks/18_live_api.ipynb` in VS Code opened through WSL. Select Python (mlop-pj). Continue with 18_live_api, 19_training_registry, 20_monitoring_recovery, 21_cicd, and 22_delivery. Each file covers one main part. Notebook 17 is complete; no rerun is needed for its upload.

| Group | What to run | Passing evidence |
|---|---|---|
| 1 | Setup, package setup, assets and deploy | Fresh DVC pull, immutable ACR image, live API, smoke and load reports |
| 2 | Submit one training job and poll registry | Completed managed job, equivalence proof, registered model tied to bundle hash |
| 3 | Monitor, then failure and alert | Dashboard with live logs, semantic failure, recovery, actual alert record |
| 4 | CI identity, GitHub settings, reviewed push and two workflow runs | Successful deploy and a failed test that blocks deploy |
| 5 | Refresh evidence and delivery | Model card, cost report, portability check, remaining items clearly listed |

Run one group at a time. Each phase writes `reports/finish-PHASE.json`. An error stops that group. Command diagnostics are in ignored tmp logs. A pending result means wait and rerun only that phase; it does not mean submit another job or create another notebook. Training and log ingestion can proceed while you set up GitHub.

The current serving bundle is kept fixed. Managed training makes a fresh fit, compares it with the selected pipeline, and exports the canonical serving bundle only after those checks pass. The training proof records what was fitted and what was exported.

Warm load uses 200 requests at concurrency 10. The target is p95 below 300 ms, not a guaranteed result. The HTTP client includes network time. The dashboard reports server time separately. Cold-start timing first checks for zero replicas; close browser API tabs while waiting.

The failure app changes mapping in staging only. The canary detects this even though readiness passes. Recovery is attempted in finally. If the failure phase errors, inspect its report and the failure app before retrying. A configured alert is not the same as a fired alert. Keep the actual alert report and screenshots.

Billing may lag behind requests. Cost per 1,000 uses the available reported resource-group cost and observed valid profile counts for the same UTC window. It is provisional, with the billing currency shown. The planning estimate is not the actual bill or a spending cap.

## Evidence to save
Save the raw-data pointer/hash, training run and proof, registry version, image digest, endpoint smoke/load/cold reports, two CI links, dashboard screenshot, fired-alert screenshot, failure/recovery report, cost calculation, model card, and final delivery status. Screenshots should show real results; do not include tokens or private account details.

## Cleanup
The reminder is 13 October 2026 at 21:15 Bangkok time. No automatic deletion runs. Save evidence before deleting the project group. This command deletes all resources in that group, including cloud data, models, compute, images, API, and monitoring:

```bash
python -m cloudlayer.cleanup --confirm-group rg-mlop-pj-492ea24d
```

Run it yourself from the project root in WSL when the resources are no longer needed. Check `reports/cleanup.json` for the verified deletion result. Keep the local evidence. Stopping apps alone does not remove ACR, storage, or monitoring charges.

## Scope limit
The prepared dashboard covers service health, model version, and uncertainty. The semantic failure demo checks mapping correctness. These are not feature-distribution drift detection. Notebook 20 includes a controlled reference/recent-window KS check and saves input-drift.json. Delivery keeps that evidence pending until it runs and detects the injected shift. This offline demonstration does not provide live drift monitoring.

If mapping failure was already detected but recovery failed, run `python -m cloudlayer.finish recovery`, then the alert phase. Recovery reuses the saved detection and restarts only the failure app. A passing readiness probe does not establish semantic recovery.
