# Registry version fix

The completed training job passed fresh-fit equivalence and bundle hash checks. Registration failed because the code used the job timestamp string 20261011-164656 as a model version. Read-only Azure lookup returned ModelNotFound, so this model has no registered version yet.

Registration now selects a small numeric version, starting at 1 and increasing from existing versions. The training job, canonical hash, and source hash stay in tags and the model still points to the same job output. Reruns reuse an existing registration only when those lineage tags match. Conflicting lineage and unfinished registrations stop rather than being overwritten.

Notebook 22 now has separate registry, alert, CI evidence, and delivery cells. Earlier outputs and metadata are preserved; the failed configuration/report/notebook are archived. Rerun the registry cell only. Do not submit another training job or rebuild the image. This review did not register a model or change cloud resources.
