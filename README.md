# Travel Style Segmentation & Drift Monitoring

ITCS355 project by Perawis Buranasing (6688012), Supitsara Tanasarnsukstid (6688121), and Atichat Kangsamut (6688193).

The service groups 24-category travel-rating profiles with K-Means. It returns a segment, cluster distance, and an uncertainty flag. Segment names are provisional; this is not a personality test.

Start with [the final submission guide](docs/FINAL_SUBMISSION.md) for the grading evidence and [the local review guide](docs/LOCAL_REVIEW.md) to run the submitted ZIP without Azure. The repository is private; GitHub links need reviewer access. The ZIP includes the pinned public dataset and canonical model, but no Git history or credentials.

Proposal responsibilities: Perawis - data, DVC, preprocessing, training, MLflow and registry; Supitsara - API, Docker, deployment, CI/CD and load testing; Atichat - dashboard, drift, alerts, failure demo, cost and model card. These are the submitted role assignments, not a separate audit of individual contributions.

## System

Blob/DVC -> Azure ML training and registry -> ACR -> Container Apps -> Azure Monitor.

GitHub Actions tests the code, downloads the verified model, builds an immutable image, and deploys only after tests pass. A separate staging app demonstrates a wrong segment mapping and recovery.

| Part | Saved evidence |
|---|---|
| Data and fresh DVC pull | reports/data-audit.json, reports/finish-assets.json |
| Managed training and registry | reports/finish-training-registry.json |
| Live API and latest CI image | reports/ci-deploy-result.json |
| Successful CI and blocked deployment | reports/ci-runs.json, reports/finish-ci-evidence.json |
| Dashboard, actual alert, failure/recovery | reports/dashboard-workbook.json, reports/finish-monitor.json, reports/finish-alert.json, reports/finish-failure.json |
| Controlled input drift | reports/input-drift.json |
| Cost and delivery checks | reports/cost-per-1000.json, docs/DELIVERY_STATUS.md |
| Model card | docs/MODEL_CARD.md; output/pdf/MODEL_CARD.pdf |
| Presentation and live demo | output/presentation/6688012_6688121_6688193_Presentation.pptx; docs/PRESENTATION.md |

The latest verified CI source commit is `9fea51a`. Both required runs use that commit:

- [Successful tests and deployment](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173375457)
- [Intentional test failure; deployment skipped](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173380800)

Documentation and evidence updates can reuse these runs while CI inputs stay unchanged. Changed source needs new runs. The check in `cloudlayer/finish_ci.py` verifies this before accepting evidence.

## Results and limits

UCI Travel Review Ratings: 5,456 raw rows, 5,454 accepted, two quarantined. Identical profiles stay in one split: 3,817 train, 817 validation, 820 test. User IDs are excluded. Data source and license are in reports/data-source.json.

K-Means k=5 had validation silhouette 0.1448 and test silhouette 0.1445. GMM validation silhouette was 0.0957. These are clustering metrics, not prediction accuracy.

Local warm p95 was 274.54 ms. Azure warm p95 was 813.77 ms from WSL, including network time; the 300 ms cloud target was not met. The first readiness request after verified zero replicas took 3,819.60 ms in one WSL HTTPS measurement. This includes network time and scale activation; it is not a cold-start percentile. See reports/finish-cold.json. The drift check is an offline controlled shift, not live feature-drift monitoring.

A separate connection-pool check measured cloud p95 624.83 ms with zero errors across 200 requests at concurrency 10. It uses HTTPX and ten concurrent warm-up requests. This differs from the first client's method and still misses 300 ms. Reproduce it with `python -m scripts.check_pooled_load` while the API is available; it makes 210 requests and requires httpx==0.28.1. Results are in reports/pooled-load.json.

The short-demo estimate is 88.89 THB, or 8.89 THB per 1,000 predictions for the assumed 10,000 predictions. Billing now reports a provisional cost row; it may not include all usage yet. Read docs/COST_REPORT.md for the separate calculation and limits.

The read-only check on 16 October reported 1.44540968 USD for the project group and 2,707 logged valid profiles over the same window: 0.53395260 USD per 1,000 profiles. This includes idle cloud time and is still provisional. At that check, 13 resources remained. See reports/billing-submission-check.json and reports/submission-preflight.json; cleanup is pending until separately verified.

## Run locally

Use WSL and Python 3.13.11. Existing users select `~/.venvs/mlop-pj/bin/python` in VS Code. For a clean review environment, follow docs/LOCAL_REVIEW.md. The original notebook setup below installs packages and rewrites a notebook lock file; it is not needed for the ZIP review.

For a fresh checkout, first check that `python3 --version` is 3.13.11, then run:

```bash
bash scripts/setup_wsl.sh
source ~/.venvs/mlop-pj/bin/activate
python -m pip install -r requirements-cloud.txt
```

Raw data and model binaries are kept out of Git. Azure Blob is private; a reviewer needs scoped access or an agreed local copy. With Azure access and the cloud packages installed:

```bash
az login
python -m dvc remote add --local --force azure azure://mlop-data/dvc
python -m dvc remote modify --local azure account_name stmloppj492ea24d
python -m dvc pull data/raw.dvc -r azure
```

In a separate fresh checkout, reproduce the local stages with `python scripts/reproduce.py all`. This runs training and writes reports and model files. It does not deploy cloud resources. Cloud notebooks 18-22 reuse the saved model and shared scripts. Read docs/FINAL_STEPS.md before running final checks.

After cloud cleanup, the private DVC remote will be gone. Download the public UCI ZIP from `source_url` in reports/data-source.json, extract google_review_ratings.csv into data/raw/, and check it with `python scripts/reproduce.py audit` before reproducing. The audit rejects a different raw SHA-256. Record which data-access option was tested for submission.

For the serving environment, install requirements-service.lock.txt and httpx==0.28.1. Run the cloud-free synthetic check with `python -m unittest tests.test_contract_ci`. Tests that use the saved real model need the artifact first; CI fetches it with `python -m cloudlayer.ci_fetch` after Azure login and project variable setup.

The API accepts exactly 24 finite ratings in [0,5], with 1-100 profiles per batch. Use the feature names in reports/bundle-manifest.json. Invalid input returns 422. An uncertain profile returns 200 with a null segment.

## Delivery

Keep real dashboard and alert screenshots, both CI links, model lineage, load/cold reports, cost calculation, and the model card. Prepare the 8-minute demo and 5-minute Q&A described in the course brief. Check the exported model card fits one page.

The 15-slide deck uses the supplied example template and saved results. Read docs/PRESENTATION.md for timing and the live API demo. The presentation PDF is in output/pdf/MLOP-PJ_Presentation.pdf; the exported model card is one A4 page.

Read docs/SUBMISSION_CHECKLIST.md for the course requirements, our own targets, and optional screenshots. The current reported cost is provisional; cloud cleanup is still required after the demo. Saved provider evidence describes the completed runs; it does not imply that cloud services will stay online after submission.

Save evidence before cleanup. The project cleanup reminder is 13 October 2026 at 21:15 Bangkok time; it does not delete anything automatically. Deleting the project group removes the API, cloud data, registry, training, and monitoring. Run the cleanup command in docs/FINAL_STEPS.md only when these resources are no longer needed.
