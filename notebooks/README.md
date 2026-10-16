# Notebook index

These notebooks preserve the development workflow and its saved outputs. For final review, start with [the project README](../README.md), [the evidence index](../docs/FINAL_SUBMISSION.md) and [the local review guide](../docs/LOCAL_REVIEW.md).

The Azure resource group has been deleted and the deployment workflow disabled after the demo. Cloud notebook cells may create resources, make API requests or require retired storage/models. Read their saved results; do not run all notebooks to inspect the submission.

Use VS Code in WSL and the project Python 3.13.11 environment when running local checks. Preserve original notebook outputs and metadata.

| Notebook | Purpose |
|---|---|
| [00_project_start.ipynb](00_project_start.ipynb) | Kernel and package checks |
| [01_data_audit.ipynb](01_data_audit.ipynb) | Public data source, pinned hash, malformed rows, zeros and duplicates |
| [02_prepare_data.ipynb](02_prepare_data.ipynb) | Quarantine and repeatable split with identical profiles kept together |
| [03_baseline_study.ipynb](03_baseline_study.ipynb) | Zero policies, K-Means settings, stability and GMM comparison |
| [04_save_model.ipynb](04_save_model.ipynb) | Bundle export, reload checks and held-out test metrics |
| [05_tracking_registry.ipynb](05_tracking_registry.ipynb) | Local MLflow study/registry and DVC versioning |
| [06_local_api.ipynb](06_local_api.ipynb) | In-process API contract and readiness |
| [07_cloud_readiness.ipynb](07_cloud_readiness.ipynb) | Local Docker/Azure tool and login checks |
| [08_docker_http.ipynb](08_docker_http.ipynb) | Initial Docker build, real HTTP smoke and load measurements |
| [09_http_recheck.ipynb](09_http_recheck.ipynb) | Remeasurement after changing HTTP client reuse |
| [10_serving_recheck.ipynb](10_serving_recheck.ipynb) | Serving optimization and local p95 recheck |
| [11_azure_preflight.ipynb](11_azure_preflight.ipynb) | Providers, regions, quotas and CLI extensions |
| [12_azure_tools.ipynb](12_azure_tools.ipynb) | Azure tooling and provider registration |
| [13_cost_plan.ipynb](13_cost_plan.ipynb) | Retail-price planning estimate |
| [14_access_quota.ipynb](14_access_quota.ipynb) | Permissions and service quota checks |
| [15_platform_preview.ipynb](15_platform_preview.ipynb) | Region policy and platform preview |
| [16_platform_deploy.ipynb](16_platform_deploy.ipynb) | Platform deployment and verification |
| [17_blob_upload.ipynb](17_blob_upload.ipynb) | Blob upload, access and round-trip hash checks |
| [18_live_api.ipynb](18_live_api.ipynb) | Deployed API and HTTP checks |
| [19_training_registry.ipynb](19_training_registry.ipynb) | Managed training and model registry |
| [20_monitoring_recovery.ipynb](20_monitoring_recovery.ipynb) | Dashboard, deliberate failure, alert and recovery |
| [21_cicd.ipynb](21_cicd.ipynb) | GitHub OIDC, workflow configuration and CI evidence |
| [22_delivery.ipynb](22_delivery.ipynb) | Cold activation, billing and original delivery evidence |

The separate [presentation demo](../output/presentation/LIVE_DEMO.ipynb) supports local mode using the supplied bundle. Follow [LOCAL_REVIEW.md](../docs/LOCAL_REVIEW.md); cloud mode no longer applies after cleanup.

Earlier latency measurements and errors are retained to explain changes. Local latency, cloud client latency and server telemetry have different measurement scopes. The final reports and guides identify the current evidence instead of treating every historical output as the latest result.
