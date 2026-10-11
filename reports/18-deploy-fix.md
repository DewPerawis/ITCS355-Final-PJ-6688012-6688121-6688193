# 18 deployment fix

The saved asset phase passed its tests, fresh DVC pull, and ACR push. Azure activity logs identify the deployment rejection: revisionSuffix is not supported for this app on the Express deployment path. The existing environment reports Succeeded and a Consumption workload profile; do not infer its behavior from those fields alone.

Removed custom revision names from the shared request used by normal deployment, CI deployment, and the staging failure/recovery demo. Azure chooses revision names. Image digests, source hashes, and Git commit receipts still record lineage.

Notebook 18 reuses its successful asset report. Phase calls run in fresh Python processes so fixes do not depend on cached notebook imports. Saved outputs and execution counts were preserved; the failed report and notebook were archived in reports/history/18-revision-suffix.

Rerun the notebook setup and assets/deploy cells. No package setup, image rebuild, DVC push, or environment replacement is required for this fix. The new deployment request still needs a real run; this review does not claim deployment succeeded.
