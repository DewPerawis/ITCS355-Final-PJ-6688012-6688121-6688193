# Remaining work preparation

Notebook 17 has saved evidence of seven uploaded files with matching SHA-256 hashes. The earlier notebook outputs were kept.

The remaining work is split by main part: 18 live API, 19 managed training and registry, 20 monitoring and recovery, 21 CI/CD, and 22 delivery. Shared scripts keep retries and reports in one place. Each notebook explains inputs, actions, outputs, passing checks, and wait conditions.

Local review: all five setup cells passed in fresh WSL processes from the notebooks folder. 52 unit tests passed and cover the mapping fault, production fault guard, selected-training equivalence, and bounded app configuration. The provider audit and Python syntax checks passed. pip dry-run resolved the Azure DVC plugin with existing constraints; resolved new dependencies are pinned. No packages were installed by this check.

Cloud code is prepared, not run evidence. The new image, endpoint, Azure training, registry registration, dashboard, alert firing, CI runs, cold start, actual cost, and cleanup still need real runs. No cloud writes, commits, pushes, or GitHub configuration were made during this preparation. The Git index was kept as found.

Read docs/RUN_FINISH.md. Start with Notebook 18 in the WSL mlop-pj kernel. Do not rerun Notebook 17 just because new code was prepared.

Notebook 20 also includes a controlled KS input-drift experiment. Its regression test uses synthetic data. The real experiment is left for the user; it does not claim live temporal drift.
