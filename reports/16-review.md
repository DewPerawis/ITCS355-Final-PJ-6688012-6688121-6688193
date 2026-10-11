# 16 review

The saved deployment failed on Key Vault: enablePurgeProtection cannot be false. Remove the property instead of sending false.

A live read-only check found Storage, ACR, Logs, Application Insights, and the Container Apps environment already created in centralindia. The Blob container operation also succeeded. ACR charges have started. Azure ML and the three identity roles were not completed.

The failed run and original template are archived in reports/history/16-key-vault-error/. Saved notebook outputs are unchanged.

The selected template is now infra/platform-recovery.json. It creates only Key Vault, Azure ML, and three scoped roles. It references the existing services and verifies their names, region, and project tags. Incremental deployment keeps services outside the recovery template. Ignore entries are omitted from what-if; Modify and Delete remain blocked.

Rerun the preview cell in 15, then both code cells in 16 after a successful preview. Template hashes force a fresh preview. The cleanup reminder remains 13 October at 14:15 UTC (21:15 Bangkok); it is not automatic deletion.

The recovery template passed a separate read-only validation and what-if with five Create changes. Thirteen targeted local tests passed. These are assistant checks; no recovery deployment has been run.

The next recovery run created Key Vault and Azure ML, plus the Key Vault and ACR roles. It failed only because the workspace Storage Blob Data Contributor role already existed under another assignment name. Exact workspace principal, storage scope, and role definition were checked with read-only ARM calls. Do not delete that role or redeploy the platform to fix the report.

The 16 script now handles this saved duplicate-role failure by verifying existing services, workspace links, identity settings, private container, and all three scoped roles. It writes reports/azure-platform-verification.json. If any check fails, it stops without deploying. If checks pass, platform_created is true, completion_mode is verified_existing, and deployment_retried is false. deployment_state remains Failed to preserve the real deployment history. Rerun only the second code cell of 16. This is a read-only recovery.

A separate assistant verification passed all 17 configuration/role checks with no Azure writes. Sixteen targeted tests passed before the repeat-check addition; the verification tests were rerun after it. This does not yet prove data-plane access or a deployed inference API.
