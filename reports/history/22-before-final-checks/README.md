# Travel Style Segmentation & Drift Monitoring

ITCS355, Faculty of ICT, Mahidol University

Group users from their 24-category rating profiles. Use K-Means as the main model and Gaussian Mixture as a comparison. Build the MLOps system on Azure.

## Start

1. Keep VS Code in WSL and select the Python environment at `~/.venvs/mlop-pj`.
2. Notebook 10 passed local correctness and the latency target. No rerun is needed.
3. The saved 16 run verified all platform services and workspace roles. ARM deployment history remains Failed due to an already-existing role; configuration verification passed.
4. Run the three code cells in 17 in order: check files, grant/check user Blob access, then upload and verify downloads.
5. Save outputs and send the result. DVC remote and Azure ML training/registry come next.

No retraining or kernel restart is needed. Notebook 11 reads cloud state only. Notebook 12 changes CLI setup and provider registration; it creates no paid resources. Notebook 13 reads public prices. Stop on errors and keep the output for review.

The setup creates `~/.venvs/mlop-pj`, installs the notebook packages, checks imports, registers a kernel, and saves installed versions in `requirements-notebook.lock.txt`. If Ubuntu lacks venv support, it installs `python3-venv` using sudo. MLflow, DVC, and Azure tools come in later steps.

## Files

| File | Use |
|---|---|
| [Proposal](proposals/current/Project%20Proposal%206688012-6688121-6688193.pdf) | Current Azure scope |
| [Plan](PLAN.md) | Detailed work plan; local only |
| [Rules](AGENT.md) | Assistant rules; local only |
| [Environment check](notebooks/00_project_start.ipynb) | Kernel and package versions |
| [Data audit](notebooks/01_data_audit.ipynb) | Raw file hash, invalid rows, zeros, and duplicates |
| [Prepare data](notebooks/02_prepare_data.ipynb) | Quarantine invalid rows and split identical profiles together |
| [Baseline study](notebooks/03_baseline_study.ipynb) | Compare zero policies, cluster counts, and seeds on validation |
| [Save model](notebooks/04_save_model.ipynb) | Save a local model bundle, report test metrics, and check reload |
| [Tracking and registry](notebooks/05_tracking_registry.ipynb) | DVC and local MLflow registration of the saved model |
| [Local API](notebooks/06_local_api.ipynb) | Readiness, prediction, bad-input, and batch checks |
| [Cloud readiness](notebooks/07_cloud_readiness.ipynb) | Read Docker and Azure login state; no resource creation |
| [Docker and HTTP](notebooks/08_docker_http.ipynb) | Build the API image, check real HTTP, and measure local warm latency |
| [HTTP recheck](notebooks/09_http_recheck.ipynb) | Correct client setup overhead and remeasure the same Docker image |
| [Serving recheck](notebooks/10_serving_recheck.ipynb) | Avoid repeated serving setup and preprocessing, then check the new image |
| [Azure preflight](notebooks/11_azure_preflight.ipynb) | Read candidate-region support, provider state, VM quota, and CLI extensions |
| [Azure tools](notebooks/12_azure_tools.ipynb) | Install the Container Apps CLI extension and register Microsoft.App |
| [Cost plan](notebooks/13_cost_plan.ipynb) | Read retail prices and estimate a short demo before credits |
| [Access and quota](notebooks/14_access_quota.ipynb) | Read effective control-plane permissions and Azure ML/Container Apps quotas |
| [Platform preview](notebooks/15_platform_preview.ipynb) | Create the project group, validate the ARM template, and preview changes |
| [Platform deployment](notebooks/16_platform_deploy.ipynb) | Create the reviewed platform; applicable Azure charges start |
| [Blob upload](notebooks/17_blob_upload.ipynb) | Grant scoped user data access, upload pinned files, and verify hashes |
| [Scope review](docs/SCOPE_REVIEW.md) | Compare the design with the course requirements |
| [Migration](docs/MIGRATION.md) | Moved files and checks |

## Team

| Member | Main work |
|---|---|
| Perawis Buranasing, 6688012 | Data, training, tracking, registry |
| Supitsara Tanasarnsukstid, 6688121 | API, Docker, deployment, CI/CD |
| Atichat Kangsamut, 6688193 | Monitoring, alerts, failure demo, cost |

These roles come from the proposal. Confirm actual owners and reviewers with the team.

## Required system

Versioned data/code, reproducible training, registry lineage, deployed inference, CI/CD, a dashboard, a working alert, cost per 1,000 predictions, a one-page model card, and a failure/recovery demo.

Planned flow: Blob/DVC -> Azure ML/MLflow/registry -> ACR -> Container Apps -> Monitor/Application Insights.

Targets: warm p95 <300 ms at concurrency 10, batch <=100, and 150 THB before credits. Report cold starts separately. These are targets, not measured results.

## Current state

The user's saved Notebook 00 result uses Python 3.13.11 in the WSL project environment. Notebook 01 ran successfully: 5,456 raw rows, 5,454 accepted rows, 2 invalid rows, 5,314 zero values, and 3 duplicate profiles. The raw SHA-256 matches the saved source report. Imports worked in Notebook 01.

Notebooks 02-04 ran successfully. Split counts are train 3,817, validation 817, and test 820, with no duplicate group crossing splits. The selected model is K-Means with 5 clusters and keep_zero. Mean validation silhouette is 0.144827; test silhouette is 0.144515. Cross-seed validation ARI is 1.0. Bundle abfd88e893ca passed reload checks. These scores indicate overlapping clusters; they are not classification accuracy or proof of user benefit.

Notebooks 05-07 ran successfully. Local MLflow model version 1 passed registry reload; raw-data DVC status was clean. The API passed 15 tests and in-process smoke checks. Docker was ready, Azure CLI was installed and logged in, and the subscription was enabled. These are saved checks, not a cloud deployment. Region, quota, permissions, and cost still need review. Segment names remain provisional. The proposal is a submission; no extra teacher approval gate is needed under the user's clarification.

Notebook 08 built the image and passed real HTTP smoke, golden predictions, and batch 100. The 200 requests at concurrency 10 had no errors, but p95 was 567.99 ms and missed the 300 ms target. After fixing repeated client/TLS setup, Notebook 09 used the same image with no errors and p95 496.01 ms, which still missed the target. Original results are preserved in `reports/history/08-initial/` and `reports/history/09-initial/`.

The serving path now caches native-library discovery and transforms each batch once. All 5,454 prepared profiles matched the earlier predictions exactly. Notebook 10 passed its 15 tests, Docker smoke, and batch 100. Its 200 requests at concurrency 10 had no errors: mean 130.33 ms, p95 274.54 ms, below the 300 ms local target. This is one local workload result, not Azure performance. The saved model and data are unchanged. The old bundle source snapshot matches the study's frozen hash. If training is rerun later, rerun 03 before 04 to record the changed source; the hash guard remains enabled. See `reports/09-review.md`.

Notebook 11's corrected user report passed at 13:03 UTC on 11 October 2026. Southeast Asia was listed, all service region checks passed, and VM quota showed 6 total cores and 4 DSv2 cores available. Microsoft.App was not registered; only the ml CLI extension was installed. The saved notebook still shows the earlier error, so save the latest output. VM quota does not prove Azure ML or Container Apps quota.

Notebook 12 hit an install timeout and slow follow-up checks. The CLI now finds containerapp 1.3.0b5. Setup reads extension metadata with az version and checks core Azure state without loading unrelated extensions. A separate read-only check completed in 2.83 seconds with no errors; Microsoft.App was still Registering. All 25 tests passed in WSL. Save a fresh user status result. Notebook 13 now has a saved user result matching the price check. The short demo estimate is 91.90 THB, using an assumed 40 THB/USD and a 60 THB reserve for unpriced services. This is not a bill or spending cap. Permissions, service quotas, omitted charges, billing exchange rate, and cleanup timing remain open. No paid cloud resources have been created by these steps.

`dvc.yaml` and `scripts/reproduce.py` define audit, prepare, study, and bundle stages. Running `dvc repro` later will rerun affected stages and update outputs; it has not been run yet. It does not create cloud resources. A remote data store and fresh-clone reproduction still need setup and verification.

The user's saved 12 status has no errors and finds both CLI extensions; Microsoft.App is still Registering. The saved 13 run completed and estimates 91.90 THB under its stated assumptions. Notebook 14 is prepared. A separate assistant read-only check found the requested control-plane actions, 20 Azure ML dedicated regional cores, 6 AML DSv2 cores, and one available Container Apps environment slot. The three new access/quota tests passed. These are not a user run of 14 or a deployed system. Container Apps environment CPU quota, policies, data access, and full costs remain open.

Write new project text and comments in short, simple English. Keep code correct and easy to read.

User run 14 completed with no failed checks, all requested control-plane actions available, sufficient AML training quota, and one Container Apps environment slot. 15 and 16 are prepared with no run results. The platform template includes eight service/storage resources and three scoped workspace identity roles. Preview runs before deployment; file changes, old previews, unrelated groups, and delete/modify previews stop the deploy step. No paid platform deployment has been run by the assistant. Final app CPU quota and full costs still need checks. See `infra/README.md`.

Six project files were moved from the student course folder with matching hashes. Teacher references, old proposals, and lab files are preserved. MLOP-PJ has its own Git repository. The local .gitignore ignores itself; historical copies are a separate issue. Do not auto-commit or push.

Current step: the saved 15 run was blocked by the allowed-region policy. Config now uses centralindia. Separate assistant validation passed; the revised plan is 88.89 THB under the same assumptions. Rerun both code cells in 15 to refresh 13/14 reports and save a new preview. Earlier outputs remain as historical results. Do not run 16 until the preview passes. See reports/15-review.md.

## Continue after 17

Use `notebooks/18_live_api.ipynb` to start. Continue with 19_training_registry, 20_monitoring_recovery, 21_cicd, and 22_delivery. The five notebooks cover the API, managed training, monitoring and recovery, CI/CD, and delivery checks in separate main parts. Read `docs/RUN_FINISH.md` and `docs/GITHUB_SETUP.md`. Saved local results and the completed Blob upload stay unchanged. Cloud runs, GitHub runs, and billing evidence still need real results.
