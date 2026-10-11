# Notebook 22 review

- The saved run has execution counts 1-6 and no cell errors. It uses the WSL mlop-pj environment with Python 3.13.11.
- Registry verification reused travel-style version 1 from the completed training job. No new training job was submitted.
- The actual alert and CI evidence checks passed.
- Cold-start measurement passed: 3,819.60 ms for the first readiness request after verified zero replicas. The image and model match the latest CI deployment. This is one client measurement, including network time and scale activation.
- Delivery ran without a cell error. Actual cost remains pending. Its billing call failed with a generic CLI error; a separate read-only check then succeeded but returned zero billing rows. The original cause is unconfirmed. Empty billing data does not prove zero cost.
- The earlier Azure warm p95 remains 813.77 ms, above the 300 ms target. Cold measurement does not replace that result.
- No Notebook 22 rerun is needed now. Retry only delivery when billing data is available. Final documentation and source changes still need publishing and CI checks for the final source commit.
