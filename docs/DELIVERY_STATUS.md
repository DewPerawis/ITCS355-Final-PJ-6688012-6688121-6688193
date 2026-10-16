# Delivery status

Post-demo cleanup: VERIFIED. [reports/cleanup.json](../reports/cleanup.json) records `cleanup_verified: true` for the project resource group. [The final status check](../reports/submission-status.json) also records `false` for group existence and the manually disabled deployment workflow. Live Azure services are retired; review uses local files and saved evidence.

## Five milestones

| Milestone | Saved status | Evidence |
|---|---|---|
| Data, training and registry | Completed runs recorded | [fresh data/model assets](../reports/finish-assets.json), [managed training/registry](../reports/finish-training-registry.json) |
| Deployed API | Deployment and HTTP checks recorded; service retired after demo | [CI deployment result](../reports/ci-deploy-result.json) |
| CI/CD | Successful deployment and intentional failure gate recorded; workflow now disabled | [CI evidence](../reports/finish-ci-evidence.json) |
| Monitoring, failure and recovery | Dashboard, actual alert and recovered staging incident recorded | [monitor](../reports/finish-monitor.json), [alert](../reports/finish-alert.json), [failure](../reports/finish-failure.json), [recovery](../reports/finish-recovery.json) |
| Delivery evidence | Documents, PDFs, validated local ZIP and cleanup evidence supplied | [validation](../reports/submission-validation.json), [cleanup](../reports/cleanup.json), [checklist](SUBMISSION_CHECKLIST.md) |

Local checks passed 59 existing system/API tests. A separately extracted ZIP passed 12 contract/API/runtime tests and the portability audit. The raw-data and canonical-model hashes match the saved manifests. Model card: one A4 page. These checks use the existing pinned WSL environment; a fresh package installation and full study rerun were not part of final review.

The latest saved cost query reports 1.44540968 USD and 2,707 logged profiles over the same window: 0.53395260 USD per 1,000 profiles. It is provisional, includes idle cloud time, and is not a final invoice. See [COST_REPORT.md](COST_REPORT.md).

## Reading historical reports

`finish-delivery.json` is the earlier operational check, before cleanup. `submission-preflight.json` records the earlier inventory of 13 resources. Their old cleanup status is retained as history. Use `cleanup.json` for the later verified deletion and `submission-validation.json` for the local review checks.

The cloud latency target was missed, cold activation is one observation, and the drift test is offline. The saved reports support completed operations, not current cloud availability.

## Owner submission actions

The repository is public. The final LMS upload/status must be confirmed by the owner. After a documentation change, commit/push the reviewed files and rebuild the companion ZIP so it contains the latest documents. These administrative actions are separate from the supplied operational evidence.
