# Submission checklist

The capstone brief requires versioned data/code, reproducible training, a registered model with lineage, deployed inference, CI/CD with tests that can fail, a dashboard, a working alert, cost per 1,000 predictions, a one-page model card, and a deliberate failure demo.

| Item | Evidence |
|---|---|
| Data/code and fresh DVC pull | reports/data-audit.json; finish-assets.json |
| Managed training and registry | reports/finish-training-registry.json |
| Deployed inference | reports/ci-deploy-result.json |
| Normal CI and deliberate failure gate | reports/finish-ci-evidence.json; ci-runs.json |
| Dashboard and actual alert | reports/dashboard-workbook.json; finish-alert.json |
| Failure and confirmed recovery | reports/finish-failure.json |
| Cost per 1,000 predictions | docs/COST_REPORT.md; reports/cost-per-1000.json |
| One-page model card | output/pdf/MODEL_CARD.pdf |
| Presentation and live demo | output/presentation/MLOP-PJ_Presentation.pptx; docs/PRESENTATION.md |

The 300 ms warm p95 target is our proposal target. It is not a fixed number in the capstone brief. Our cloud result misses it; report the result and explain the measurement scope.

The brief requires a working dashboard and alert, but does not specify Portal screenshots as the only acceptable proof. Saved provider responses, logs, and a live demo support these claims. Screenshots are useful extra evidence.

The brief requires documented cost per 1,000 predictions. Lab 5 separately requires actual cost from billing. We now have a reported cost row, but billing can still be incomplete. Keep the estimate and provisional reported cost separate; do not call the reported row a final invoice.

Final CI evidence must cover the submitted source. A later commit that changes only documentation/evidence can reuse the tested commit if all CI inputs are unchanged. Changed or uncommitted CI inputs require new runs.

Rehearse the 8-minute presentation and allow 5 minutes for questions. Save evidence before cleanup, then remove the project cloud resources after the live demo and verify removal. Cleanup is still required; the reminder does not delete anything.

Sources checked: the instructor's Capstone Project Brief, the course specification's Rubric Scoring sheet, and Lab 5 Task 5. The rubric has five criteria worth six marks each. This checklist does not guarantee a grade.
