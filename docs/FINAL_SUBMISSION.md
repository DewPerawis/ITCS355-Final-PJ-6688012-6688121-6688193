# Final submission guide

**Travel Style Segmentation & Drift Monitoring - ITCS355**

Team: Perawis Buranasing (6688012), Supitsara Tanasarnsukstid (6688121), Atichat Kangsamut (6688193).

## Project description

This project builds an operational travel-preference segmentation service. A FastAPI endpoint accepts a complete 24-category rating profile and returns its K-Means segment, cluster distance, uncertainty flag and model version. The system connects versioned data and reproducible training to model registration, tested deployment, monitoring, alerting and recovery. A Gaussian Mixture Model provides a comparison. The focus is the operational system; clustering metrics are not prediction accuracy.

## Start here

Read [README.md](../README.md) for the project overview, checked requirements and path descriptions. Open the [presentation](../output/presentation/6688012_6688121_6688193_Presentation.pdf) and [one-page model card](../output/pdf/MODEL_CARD.pdf), then follow [LOCAL_REVIEW.md](LOCAL_REVIEW.md) for local API checks.

The companion ZIP includes the pinned public CSV and canonical model as well as source and saved evidence. It excludes credentials, caches and Git history. `SUBMISSION_MANIFEST.json` inside the ZIP records its base commit, tested CI commit and file hashes. Git-only checkouts do not include the CSV/model binaries.

Repository: [DewPerawis/MLOP-PJ](https://github.com/DewPerawis/MLOP-PJ). It was private at the final check; history and Actions need reviewer access. The ZIP can be reviewed without GitHub or Azure access.

## Rubric and evidence index

| Rubric | Component | Main evidence |
|---|---|---|
| R1 - Reproducible ML Pipeline | Data/code versioning and deterministic preparation | [DVC pointer](../data/raw.dvc), [source/hash](../reports/data-source.json), [audit](../reports/data-audit.json), [fresh pull](../reports/finish-assets.json), Git history |
| R1 | Automated training and registry lineage | [runner](../scripts/reproduce.py), [pipeline](../dvc.yaml), [selection](../reports/selection.json), [fresh-fit proof](../reports/azure-training-proof.json), [managed registry](../reports/finish-training-registry.json) |
| R2 - Deployment & CI/CD | Inference, successful deploy, failing test gate | [API](../service/app.py), [workflow](../.github/workflows/ci.yml), [HTTP/image checks](../reports/ci-deploy-result.json), [CI evidence](../reports/finish-ci-evidence.json) |
| R3 - Monitoring & Reliability | Dashboard, telemetry and real alert | [workbook](../reports/dashboard-workbook.json), [charts](../reports/dashboard-chart-update.json), [telemetry](../reports/azure-telemetry.json), [fired/resolved alert](../reports/finish-alert.json) |
| R4 - Failure Handling & Technical Defense | Staging semantic failure, detection and recovery | [failure](../reports/finish-failure.json), [recovery](../reports/finish-recovery.json), [regression tests](../tests/test_api.py) |
| R5 - Documentation & Presentation | README, costs, model card and presentation | [cost report](COST_REPORT.md), [billing/count responses](../reports/billing-submission-check.json), [model card](../output/pdf/MODEL_CARD.pdf), [presentation](../output/presentation/6688012_6688121_6688193_Presentation.pdf) |
| Post-demo delivery | Review copy and cloud shutdown | [local validation](../reports/submission-validation.json), [verified cleanup](../reports/cleanup.json), [local guide](LOCAL_REVIEW.md) |

Use [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) for the individual required components. The brief assigns 30 marks to the repository and 15 to the demo/defense. The checklist identifies evidence; it does not assign a score.

## CI and failure evidence

- [Successful tests and deployment](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173375457)
- [Deliberate failed test with deployment skipped](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173380800)

Both use source commit `9fea51ae4e81251ac358a2c62139df591688275d`. Their conclusions and job outcomes were checked on 16 October. The expected failed run proves the CI gate. The separate staging incident swaps segment names, detects a semantic regression and confirms recovery; it is not the same experiment.

Later documentation/report commits retain these runs as evidence only while CI inputs match the tested source. The workflow is now manually disabled after the demo. No new deployment is required to inspect this submission.

## Final cloud status

Post-demo cleanup: VERIFIED. [cleanup.json](../reports/cleanup.json) records the project group and `cleanup_verified: true`. A separate read-only check confirmed that the group does not exist. The API, private DVC remote, registry and live dashboard have been retired. Use the supplied local model and saved evidence.

[submission-preflight.json](../reports/submission-preflight.json) is the earlier inventory before cleanup; it correctly records 13 resources at that earlier time. It is historical evidence, not the current state. [DELIVERY_STATUS.md](DELIVERY_STATUS.md) describes the current saved status.

## Results and limitations

Cloud warm p95 missed the team's 300 ms target. Cold activation is one request, not a percentile. Drift is an offline controlled input shift. Segment names are provisional and distance is not a probability. Azure Monitor recorded an alert event; email notifications were not configured.

The latest saved billing query reports 1.44540968 USD and 2,707 logged valid profiles over the same window, or 0.53395260 USD per 1,000 profiles. It includes idle cloud time and remains provisional. The earlier demo-period amount is preserved separately. This is not a final invoice or proof of a before-credit budget limit.

Local validation used the existing pinned WSL environment: 59 system/API tests and 12 checks on an extracted ZIP passed. The final review did not test a fresh package installation or rerun the full model study. See [the validation report](../reports/submission-validation.json).

## Submission format

Use the repository link plus the companion ZIP in the LMS. The presentation and model-card PDFs can also be attached separately; both are in the ZIP. The LMS screenshot allows online text and files, with 100 MB maximum file size and up to 20 files.

The owner must ensure instructor access to private GitHub links, commit/push any final documentation changes, upload the current ZIP, and check the LMS status. The documentation review does not verify an LMS submission.
