# Notebook 20 review

The controlled input-drift test detected the injected change and did not flag the normal test window. This is an offline controlled test, not observed temporal drift.

Dashboard creation passed. The saved failure was detected, and the recovery-only run returned a passing semantic canary twice. No new failure injection is needed.

Live Azure review found an actual Fired alert. The evidence checker previously matched only the short/display rule name, while Azure returned a full resource ID. It now accepts the exact project rule ID, preserves group ownership checks, and requires a Fired or Resolved condition. The prior pending report was archived and the alert evidence refreshed using read-only Azure requests. 57 local tests and the portability audit passed.

Continue with Notebook 21 setup and ci-setup, then docs/GITHUB_SETUP.md. Training/registry, cold-start, latency target, CI runs, billing, and cleanup remain separate evidence items. No cloud configuration, commit, or push was performed during this review.
