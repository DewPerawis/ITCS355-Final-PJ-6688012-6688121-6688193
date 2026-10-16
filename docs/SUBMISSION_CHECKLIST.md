# Submission checklist

This checklist maps the capstone requirements to supplied files. Checked items refer to implementation and saved evidence, not a guaranteed grade or a currently running cloud service.

- [x] Versioned code: repository Git history and the source commit in [CI evidence](../reports/finish-ci-evidence.json).
- [x] Versioned data: [DVC pointer](../data/raw.dvc), [source/license/hash](../reports/data-source.json), [audit](../reports/data-audit.json), and [fresh pull](../reports/finish-assets.json).
- [x] Automated reproducible training: [stage runner](../scripts/reproduce.py), [pipeline](../dvc.yaml), [selection](../reports/selection.json), and [training proof](../reports/azure-training-proof.json).
- [x] Registered model and lineage: [registry result](../reports/finish-training-registry.json) and [bundle manifest](../reports/bundle-manifest.json).
- [x] Deployed inference: [real HTTP and image verification](../reports/ci-deploy-result.json).
- [x] CI/CD with a failing gate: [workflow](../.github/workflows/ci.yml), [successful run](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173375457), and [deliberate test failure with skipped deploy](https://github.com/DewPerawis/MLOP-PJ/actions/runs/38173380800).
- [x] Dashboard: [workbook](../reports/dashboard-workbook.json), [chart evidence](../reports/dashboard-chart-update.json), and [telemetry](../reports/azure-telemetry.json).
- [x] Working alert: [actual fired/resolved alert](../reports/finish-alert.json). Email notifications were not configured.
- [x] Deliberate failure and recovery: [failure](../reports/finish-failure.json), [recovery](../reports/finish-recovery.json), and [regression tests](../tests/test_api.py).
- [x] Cost per 1,000 predictions: [cost report](COST_REPORT.md) and [latest saved billing/count evidence](../reports/billing-submission-check.json).
- [x] One-page model card: [A4 PDF](../output/pdf/MODEL_CARD.pdf).
- [x] Presentation materials: [PDF](../output/presentation/6688012_6688121_6688193_Presentation.pdf), [PPTX](../output/presentation/6688012_6688121_6688193_Presentation.pptx), and [demo notebook](../output/presentation/LIVE_DEMO.ipynb).
- [x] Cleanup after the demo: [resource-group deletion verified](../reports/cleanup.json).
- [x] Local review instructions and tested files: [review guide](LOCAL_REVIEW.md), [validation report](../reports/submission-validation.json), and the accompanying ZIP with pinned data/model files.

## Scope and interpretation

The cloud warm p95 target of 300 ms belongs to the proposal; the saved cloud results miss it. The cold result is one observation. The drift experiment is offline. Costs remain provisional; the earlier cost-per-1000.json is a historical demo-period result, not the latest reported total.

The brief requires a dashboard and working alert, but does not prescribe Portal screenshots as the only proof. Saved provider responses, logs and the completed demonstration support the operational claims. Cloud resources have now been removed; use the local review guide instead of the old endpoint.

The repository criteria are R1-R5 at six marks each (30 marks). Demo and defense are separate (15 marks). Source: the instructor's capstone brief and course specification reviewed for this project.

The owner must still ensure the instructor can access the private repository if its links are used, upload the final files, and verify the LMS submission status. These administrative steps are not claimed complete by this checklist.
