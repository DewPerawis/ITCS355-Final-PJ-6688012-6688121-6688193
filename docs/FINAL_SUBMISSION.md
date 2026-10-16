# Final submission guide

Travel Style Segmentation & Drift Monitoring - ITCS355.

Team: Perawis Buranasing (6688012), Supitsara Tanasarnsukstid (6688121), Atichat Kangsamut (6688193).

## Start here

The repository contains the system, notebooks and saved operational evidence. The companion ZIP is a working-tree review snapshot with the pinned public CSV and tested model bundle. It excludes Git history, credentials, caches and internal planning files. Use LOCAL_REVIEW.md to check it without Azure.

Repository: https://github.com/DewPerawis/MLOP-PJ. It was private at the 16 October check; the instructor needs access to inspect its history or Actions. The attached ZIP can be reviewed without that access.

## Required components and evidence

| Rubric | Required component | Files |
|---|---|---|
| R1 | Versioned code/data and fresh DVC pull | Git history; data/raw.dvc; reports/data-source.json; data-audit.json; finish-assets.json |
| R1 | Reproducible training and registry lineage | scripts/reproduce.py; dvc.yaml; reports/selection.json; azure-training-proof.json; finish-training-registry.json |
| R2 | Inference and CI/CD | service/; .github/workflows/ci.yml; reports/ci-deploy-result.json; finish-ci-evidence.json |
| R3 | Dashboard and a working alert | reports/dashboard-workbook.json; dashboard-chart-update.json; azure-telemetry.json; finish-alert.json |
| R4 | Deliberate failure and recovery | reports/finish-failure.json; finish-recovery.json; tests/test_api.py |
| R5 | Cost per 1,000 predictions | docs/COST_REPORT.md; reports/billing-submission-check.json; cost-per-1000.json |
| R5 | One-page model card and presentation | output/pdf/MODEL_CARD.pdf; output/presentation/6688012_6688121_6688193_Presentation.pdf |

All reports above are under reports/ unless a full path is given. Historical error reports are retained when notebooks use them or they explain the recovery history. Saved results describe past runs, not ongoing service availability.

The brief assigns 30 marks to the repository (five criteria at six marks each) and 15 to the demo/defense. It requires no separate report length or compulsory ZIP format. The LMS accepts online text and files; its screenshot shows a maximum file size of 100 MB and up to 20 files.

## CI evidence

- Successful tests and deployment: https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173375457
- Deliberate failed test, deployment skipped: https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173380800

Both use source commit 9fea51ae4e81251ac358a2c62139df591688275d. The 16 October read-only check confirmed the run conclusions and job outcomes. Documentation and report changes do not replace these runs. Changed CI inputs need new evidence.

## Results and limitations

Cloud warm p95 missed the team's 300 ms target. The cold-start result is one request, not a percentile. The drift test is an offline controlled input shift. Segment names are provisional and distance is not a probability. None of these results is prediction accuracy.

The 16 October billing query reports 1.44540968 USD and 2,707 logged profiles over the same window, or 0.53395260 USD per 1,000 profiles. This includes idle cloud time and remains provisional. Keep the earlier demo-period result separate.

## Remaining submission actions

- Preserve the evidence and test the ZIP before removing cloud storage and the registry.
- Disable automatic deployment after the demo, then remove and verify the project resource group. See FINAL_STEPS.md. At the 16 October check, 13 resources remained; no cleanup was performed by the review.
- Add reports/cleanup.json only after the deletion check succeeds. An empty-resource-list screenshot is useful supporting evidence.
- Review, commit and push the selected files. Do not assume local changes are already on GitHub.
- Give the instructor access if the GitHub link is used. Attach the ZIP as a review copy.
- Save the LMS submission and check its final status. The review has not submitted anything to the LMS.

## Deadline evidence

The screenshot shows Sunday 18 October 2026 at 23:59. A separate note says "before Friday 18", which conflicts with the displayed weekday. Confirm that note with the instructor; finishing on Friday 16 October avoids relying on the later interpretation.
