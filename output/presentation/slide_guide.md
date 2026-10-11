# Presentation guide

15 slides. Planned talk: 8 minutes. Q&A: 5 minutes.

Use `docs/PRESENTATION.md` for the live demo. English slides and notes. No speaker split is assigned.

## Slide 1: Travel Style Segmentation & Drift Monitoring

Time: 15 seconds.

**Text in slide:**

TRAVEL STYLE SEGMENTATION
& DRIFT MONITORING

ITCS355 - Machine Learning Operations

Perawis Buranasing (6688012)
Supitsara Tanasarnsukstid (6688121)  |  Atichat Kangsamut (6688193)

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

15 seconds. Introduce our team and the travel profile service. We focus on the working MLOps system.

**Source / number check:**

README.md; example.pptx, slide 1

## Slide 2: ONE PROFILE, A SIMPLE TRAVEL SEGMENT

Time: 45 seconds.

**Text in slide:**

ONE PROFILE,
A SIMPLE TRAVEL SEGMENT

A travel platform can use rating profiles to group similar interests.

INPUT

24 category ratings [1]
Each value: 0-5

MODEL

K-Means, k=5
Shared preprocessing

OUTPUT

Segment + distance
Uncertainty + version

Segment names are provisional. This is a preference tool, not a personality test.

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

A travel platform can group users by their rating profiles. We take 24 category ratings and return a segment, distance, uncertainty flag, and model version. Names are provisional; we have not tested recommendation quality with users.

**Source / number check:**

docs/MODEL_CARD.md; reports/bundle-manifest.json; UCI [1]

**Citation:**

[1] S. Renjith, "Travel Review Ratings," UCI dataset, 2018.

## Slide 3: FROM VERSIONED DATA TO A MONITORED API

Time: 40 seconds.

**Text in slide:**

FROM VERSIONED DATA
TO A MONITORED API

DATA

Git + DVC
Azure Blob

TRAIN

Azure ML
MLflow

REGISTER

Model version
Bundle hash

SHIP

Actions
ACR image

SERVE

FastAPI
Container Apps

OBSERVE

Azure Monitor + Log Analytics
Dashboard, semantic alert, model version

Tests gate deployment.
Failure checks feed back into tests.

Azure region: centralindia  |  Provider code: cloudlayer/

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

Follow the arrows from versioned data to the live endpoint. Azure ML trains and registers the model. Actions checks the code and deploys an immutable ACR image. Monitor records requests and checks the semantic canary. Cloud-specific code stays in cloudlayer.

**Source / number check:**

README.md; docs/reference/course/project/project-brief.md [2]

**Citation:**

[2] ITCS355, "Capstone Project Brief," course handout.

## Slide 4: ONE VERSIONED DATASET, ONE REPEATABLE PIPELINE

Time: 25 seconds.

**Text in slide:**

ONE VERSIONED DATASET,
ONE REPEATABLE PIPELINE

5,456

Raw rows

5,454

Accepted rows

2

Quarantined rows

CC BY 4.0 [1]  |  Raw SHA-256 + DVC pointer  |  Seed 42
Train-only imputation/scaling. Identical profiles stay in one split.

**Visual:**

[data-split.png](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/figures/data-split.png)

`output/presentation/figures/data-split.png`; generated from reports/prepared-data.json.

**Speaker notes:**

UCI Travel Review Ratings is licensed CC BY 4.0. We quarantined two malformed rows, removed user IDs from features, and kept duplicates in one split. We kept zeros as supplied and fit preprocessing only on training data. The fresh DVC pull passed.

**Source / number check:**

reports/data-audit.json; prepared-data.json; selection.json; UCI [1]

**Citation:**

[1] S. Renjith, "Travel Review Ratings," UCI dataset, 2018.

## Slide 5: THE SAME BUNDLE REACHES THE API

Time: 25 seconds.

**Text in slide:**

THE SAME BUNDLE
REACHES THE API

MANAGED TRAINING

Azure ML job: Completed
Fresh-fit equivalence: passed
Registry: travel-style, version 1

SERVING BUNDLE

Preprocessing + feature order
Centers + mapping + thresholds
Hash and golden checks at startup

Model version: abfd88e893ca

Bundle SHA-256: 71f3ba41b4b964f5...
CI image digest: b55cd10aba3f...

Immutable images use one canonical bundle.

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

The managed training job completed and the registered model is travel-style version 1. Azure checks a fresh fit against the selected model before exporting the canonical bundle. Startup checks the bundle hash and golden predictions. K-Means test silhouette is 0.1445; model quality is not the main capstone focus.

**Source / number check:**

reports/finish-training-registry.json; bundle-manifest.json; ci-deploy-result.json

## Slide 6: LIVE DEMO: VALID AND UNEXPECTED INPUT

Time: 90 seconds.

**Text in slide:**

LIVE DEMO:
VALID AND UNEXPECTED INPUT

| Request | Expected / verified |
| --- | --- |
| Valid 24-field profile | 200 + segment |
| Missing fields / invalid rating | 422, clear validation error |
| Batch of 100 profiles | 200; golden check passed |
| Semantic canary | 200; predictions match |

SAVED REAL HTTP RESPONSE

{
  "segment": "Segment 1",
  "cluster_id": 0,
  "distance": 4.1435,
  "uncertain": false,
  "model_version": "abfd88e893ca"
}

Exactly 24 named, finite ratings in [0,5]. A valid uncertain profile returns a null segment.

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

Live demo: open Notebook 22 and run the small smoke check in PRESENTATION.md. Show one valid prediction, an incomplete profile returning 422, and a batch of 100. A valid uncertain profile returns 200 with a null segment. The example shown here is a real HTTP response saved from the live API, not a live screenshot.

**Source / number check:**

output/presentation/evidence/api-demo.json; service/schemas.py

## Slide 7: FAILED TESTS BLOCK DEPLOYMENT

Time: 35 seconds.

**Text in slide:**

FAILED TESTS
BLOCK DEPLOYMENT

NORMAL RUN

Tests: success
Deploy: success
Real HTTP smoke: passed

DELIBERATE FAILURE

Tests: failure
Deploy: skipped
Failed code was not shipped

Open GitHub Actions run 38166188586

Open GitHub Actions run 38166197980

Same tested source commit: 1e0bd12  |  OIDC login + limited roles  |  Immutable image

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

Both saved runs use commit 1e0bd12. In the normal run, tests and deployment passed. In the deliberate failure run, tests failed and deployment was skipped. Click the run links to show the actual jobs. These runs do not verify later local code changes.

**Source / number check:**

reports/ci-runs.json; reports/ci-deploy-result.json; .github/workflows/ci.yml

## Slide 8: THE API WORKS; CLOUD LATENCY MISSES OUR TARGET

Time: 25 seconds.

**Text in slide:**

THE API WORKS;
CLOUD LATENCY MISSES OUR TARGET

WARM TEST

200 requests
Concurrency: 10
Errors: 0 in both runs

COLD REQUEST

3.82 seconds
After verified zero replicas
One WSL HTTPS sample

**Visual:**

[warm-latency.png](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/figures/warm-latency.png)

`output/presentation/figures/warm-latency.png`; generated from reports/serving-recheck/local-load.json; reports/azure-load.json.

**Speaker notes:**

Each warm test used 200 requests, concurrency 10, batch size 1, and excluded 10 warm-up requests. Both had zero errors. Azure timing includes the WSL network path. Local and cloud warm p95 are different scopes. Cold start is one first readiness request after verified zero replicas, not a percentile.

**Source / number check:**

reports/serving-recheck/local-load.json; azure-load.json; finish-cold.json

## Slide 9: MONITOR REQUESTS AND CHECK PREDICTION MEANING

Time: 25 seconds.

**Text in slide:**

MONITOR REQUESTS
AND CHECK PREDICTION MEANING

DASHBOARD

MLOP Travel Style
Requests, errors, latency
Model version in logs

ACTUAL ALERT

Semantic failure detected
Alert fired, then resolved
Email is not configured

Saved Log Analytics results; application timing, not client HTTPS latency.

**Visual:**

[monitor-logs.png](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/figures/monitor-logs.png)

`output/presentation/figures/monitor-logs.png`; generated from reports/azure-telemetry.json.

**Speaker notes:**

This chart uses actual saved Log Analytics bins, not an Azure Portal screenshot. The dashboard is MLOP Travel Style. Logs contain derived counts, status, latency, and model version rather than full profiles. Logged p95 is application timing and must not be compared directly with client HTTPS p95. An actual semantic alert fired and later resolved; email notification is not configured.

**Source / number check:**

reports/azure-telemetry.json; finish-monitor.json; finish-alert.json

## Slide 10: A WRONG SEGMENT MAPPING TRIGGERED DETECTION AND RECOVERY

Time: 45 seconds.

**Text in slide:**

A WRONG SEGMENT MAPPING
TRIGGERED DETECTION AND RECOVERY

Controlled fault in the separate staging app: wrong cluster-to-segment mapping.

INJECT

16:54:22 UTC
Wrong mapping

DETECT

16:54:52 UTC
Canary: 503

ALERT

16:56:39 UTC
Actual alert fired

RECOVER

17:02:08 UTC
Canary: 200

Detection to confirmed recovery: 7 min 16.4 sec, including the failed first recovery attempt.

Fix: restore config, restart staging, confirm the canary twice, and keep a regression test.
Saved failure evidence. Arrows show event order, not equal time gaps.

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

This is saved failure evidence from a separate staging app. We changed the segment mapping; the canary returned 503. The first recovery attempt failed, so the total detection-to-confirmed-recovery time was about seven minutes sixteen seconds. We restored configuration, stopped and started staging, and checked the semantic canary twice. The actual alert is separate evidence. The failure was added to regression checks.

**Source / number check:**

reports/finish-failure.json; finish-alert.json; tests/test_api.py

## Slide 11: A CONTROLLED SHIFT IS DETECTED OFFLINE

Time: 20 seconds.

**Text in slide:**

A CONTROLLED SHIFT
IS DETECTED OFFLINE

CONTROLLED TEST

Reference: 1,908 rows
Recent sample: 200 rows
100 calibration rounds

Shift: +1.5 in four ratings,
clipped to [0,5].

Offline input drift only.
No concept-drift claim.

**Visual:**

[controlled-drift.png](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/figures/controlled-drift.png)

`output/presentation/figures/controlled-drift.png`; generated from reports/input-drift.json.

**Speaker notes:**

We used a maximum feature-wise KS statistic. The reference has 1,908 rows and the recent sample has 200. One hundred calibration rounds set the threshold. Adding 1.5 to the first four features, clipped to 0-5, caused the alert condition. This is an offline controlled test, not observed temporal drift or evidence of concept drift.

**Source / number check:**

reports/input-drift.json; monitoring/drift.py

## Slide 12: COST PER 1,000 PREDICTIONS: THE ESTIMATE AND ITS LIMITS

Time: 30 seconds.

**Text in slide:**

COST PER 1,000 PREDICTIONS:
THE ESTIMATE AND ITS LIMITS

PLANNED COST

8.89 THB / 1,000
Assume 10,000 predictions
One prediction per request

ACTUAL BILL

Not available yet
Budget is a target
Keep billing and usage aligned

Assumptions: 40 THB/USD; training 1 h; app active 2 h; ACR 2 days. No credits applied.

**Visual:**

[planned-cost.png](C:/Users/SN23341J001185/Documents/MyWork/ICT/ICTYear4_1/MLop/public_teaching_mlaiops/course/MLOP-PJ/output/presentation/figures/planned-cost.png)

`output/presentation/figures/planned-cost.png`; generated from reports/azure-cost-plan.json.

**Speaker notes:**

The short-demo plan totals 88.89 THB, including a 60 THB reserve. At 10,000 planned predictions, that is 8.89 THB per 1,000. The plan assumes 40 THB per USD, one training VM-hour, two app-active hours, and two ACR days. This is before credits. Actual billing is still unavailable, so we cannot claim the final spend or a real spending cap.

**Source / number check:**

reports/azure-cost-plan.json; cost-per-1000.json; docs/COST_REPORT.md

## Slide 13: WHAT ANOTHER WEEK WOULD IMPROVE

Time: 45 seconds.

**Text in slide:**

WHAT ANOTHER WEEK
WOULD IMPROVE

| Priority | Next action |
| --- | --- |
| Cloud warm latency | Measure network vs. application time; retest p95 |
| Actual cost evidence | Match the bill and prediction count over one window |
| Live feature drift | Add rolling windows when current data is available |
| Final delivery | Review labels, capture Portal evidence, retest final code |

Current limits: provisional labels, unknown zero meaning, and no user-quality study.

Save evidence before cleanup. Remove cloud resources after the final demo.

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

Our first priorities are the unmet latency target and the missing actual cost evidence. Measure from a closer client and separate network time from application time before changing replicas or spending more. Recheck billing over the same usage window. Add live feature windows only when we have valid current data. Review labels and prepare real Portal screenshots. Retest later source changes in CI and save evidence before cloud cleanup.

**Source / number check:**

reports/finish-delivery.json; docs/DELIVERY_STATUS.md; docs/FINAL_STEPS.md

## Slide 14: REFERENCES

Time: 5 seconds.

**Text in slide:**

REFERENCES

[1] S. Renjith, "Travel Review Ratings," UCI Machine Learning Repository, 2018.
DOI: 10.24432/C5C31Q. License: CC BY 4.0.

[2] ITCS355, "Capstone Project Brief," course/project/project-brief.md.
Presentation: 8 minutes + 5 minutes of questions.

[3] MLOP-PJ team, "Project reports and CI runs."
Data, registry, API, load, alert, recovery, drift, and cost evidence.

Dataset: https://doi.org/10.24432/C5C31Q

Repository: https://github.com/DewPerawis/MLOP-PJ (access required)

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

The dataset citation and course brief support the scope. Our measurements and operational claims come from the listed project reports. GitHub evidence requires repository access.

**Source / number check:**

UCI dataset page; course brief; project reports and CI runs

## Slide 15: Thank you

Time: 10 seconds.

**Text in slide:**

THANK YOU

**Visual:**

Use the editable diagram, table, or report panels already in this slide. Keep the supplied template background.

**Speaker notes:**

10 seconds. Thank the audience. Open the API and evidence reports for the five-minute Q&A.

**Source / number check:**

example.pptx, slide 15
