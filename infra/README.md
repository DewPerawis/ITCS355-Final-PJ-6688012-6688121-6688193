# Azure platform templates

The templates document the infrastructure used during the project. The resource group has since been removed; [cleanup evidence](../reports/cleanup.json) verifies deletion. Reviewing the project does not require applying these templates.

| File | Purpose |
|---|---|
| [platform.json](platform.json) | Base platform: Storage/private Blob container, Basic ACR, Log Analytics, Key Vault, Application Insights, Azure ML workspace/identity, roles and Container Apps environment |
| [platform-recovery.json](platform-recovery.json) | Incremental recovery template used after an earlier deployment failure |

The prediction apps, managed training, model registration, monitoring and CI/CD are implemented by the later notebooks and [cloudlayer](../cloudlayer/) modules. See [the evidence index](../docs/FINAL_SUBMISSION.md) for their completed run reports.

The selected service region was centralindia after subscription-policy checks. Applying templates can create paid resources and requires a fresh account, policy, quota, permission and price review. The proposal budget and planning estimate are not spending caps. Resource tags are reminders, not automatic cleanup.
