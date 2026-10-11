# Azure platform

15 creates the project group and runs Azure validation/what-if. 16 applies the same files after a passing preview. The assistant has not run either cloud operation.

The template includes Storage and a private Blob container, Basic ACR, shared Log Analytics, RBAC Key Vault, Application Insights, an identity-based Azure ML workspace, and a Consumption Container Apps environment. The workspace identity gets Blob Data Contributor, Key Vault Secrets Officer, and AcrPull only on these project resources.

ACR starts a daily charge after deployment. Other charges depend on usage. The 150 THB budget and 88.89 THB estimate are planning values, not a cap. The logs cap is 0.1 GB/day; it is not a spending guarantee. The removeAfter tag is a reminder; it does not delete resources.

There is no training compute, prediction app, Dedicated profile, private endpoint, or deletion in this template. These come after platform and quota checks. DVC, cloud training, CI/CD, monitoring, and failure recovery still need integration and real results.

[ARM what-if](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-what-if) | [Workspace identity auth](https://learn.microsoft.com/en-us/azure/templates/microsoft.machinelearningservices/2026-03-01/workspaces) | [Container Apps billing](https://learn.microsoft.com/en-us/azure/container-apps/billing)

Use centralindia. The subscription policy rejects southeastasia for services. An existing owned group may keep its metadata location there. Notebook 15 refreshes prices and quota before preview.

Recovery after the saved 16 failure uses platform-recovery.json: only Key Vault, Azure ML, and three roles. The five existing services are checked and retained with incremental deployment. Run a fresh 15 preview before retrying 16.
