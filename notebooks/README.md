# Notebooks

Use VS Code in WSL and select **MLOP-PJ (WSL)**.

- `00_project_start.ipynb`: check the kernel and package versions.
- `01_data_audit.ipynb`: download the public UCI file, save its hash, and check invalid rows, zeros, and duplicates.
- `02_prepare_data.ipynb`: quarantine bad rows and make a repeatable split by identical profile groups.
- `03_baseline_study.ipynb`: compare zero policies and K-Means settings on validation; fit one GMM comparison.
- `04_save_model.ipynb`: save the selected pipeline, check reload, and report held-out test metrics.
- `05_tracking_registry.ipynb`: record the completed study, version raw data with DVC, and register the saved bundle in local MLflow.
- `06_local_api.ipynb`: check the API contract and readiness with an in-process client.
- `07_cloud_readiness.ipynb`: check Docker and Azure CLI/login state without creating resources.
- `08_docker_http.ipynb`: build the saved model into Docker, check real HTTP, and measure local warm latency.
- `09_http_recheck.ipynb`: reuse the same image and remeasure after fixing repeated client setup.
- `10_serving_recheck.ipynb`: build the optimized serving source and recheck correctness and local latency.
- `11_azure_preflight.ipynb`: read service providers, candidate-region support, VM quota, and CLI extensions.
- `12_azure_tools.ipynb`: install the missing Container Apps CLI extension and register Microsoft.App.
- `13_cost_plan.ipynb`: read retail prices and estimate a short demo before credits.
- `14_access_quota.ipynb`: read control-plane permissions and Azure ML/Container Apps quotas.
- `15_platform_preview.ipynb`: refresh prices/quota for centralindia, check the region policy, and preview without applying. Rerun both code cells after the region fix.
- `16_platform_deploy.ipynb`: deploy or verify the existing platform after the duplicate-role failure.
- `17_blob_upload.ipynb`: grant user Blob access, upload pinned data/model files, and verify downloaded hashes.

00-10 have saved results. Notebook 10 passed the local p95 target at 274.54 ms with no errors. The new report from 11 passed; save the notebook to replace its old displayed error. No retraining or rerun of 10 is needed. Local results are not Azure deployment results.

Keep the same WSL kernel. The cost estimate uses an assumed exchange rate and reserve; it is not a bill or spending cap. Earlier read-only checks created no paid resources; 16 has now created services and charges can apply.

The earlier 12 timeout is fixed. The saved status has no errors and finds containerapp 1.3.0b5. Do not reinstall the extension. A pending provider is not an error.

The saved user status from 12 has no errors and 13-14 have completed. Run 15 next. If its validation and preview pass, review the resource list before running 16. Stop on errors, Modify, or Delete changes. 16 creates services and can incur charges; it does not deploy the prediction API yet. Region availability and quota are not a guarantee of successful deployment.

Run one part, review the result, then continue. Keep saved outputs. Write short, simple English and useful comments.

Use notebooks for exploration. Move agreed code into `src/` so tests and pipelines share it.

Lab 5 Part A overlaps with the project's pipeline, identity, and cost work. The project also uses ideas from Labs 1-4. Lab 5 Part B does not make an LLM or a second provider a project requirement. See the course brief in `../../project/project-brief.md`.

Current: the saved 16 verification passed. Run all three code cells in 17 in order. Stop if Blob access fails.

## Continue after 17

Use `notebooks/18_live_api.ipynb` to start. Continue with 19_training_registry, 20_monitoring_recovery, 21_cicd, and 22_delivery. The five notebooks cover the API, managed training, monitoring and recovery, CI/CD, and delivery checks in separate main parts. Read `docs/RUN_FINISH.md` and `docs/GITHUB_SETUP.md`. Saved local results and the completed Blob upload stay unchanged. Cloud runs, GitHub runs, and billing evidence still need real results.
