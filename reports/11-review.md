# 10 and 11 review

## Corrected user report

The user's new report at 13:03 UTC on 11 October passed with no failed checks. Region checks passed; VM quota showed 6 total cores and 4 DSv2 cores available. Microsoft.App was NotRegistered and only the ml extension was installed. The notebook file still contains its earlier error output; save the latest result. No paid resources were created. Notebooks 12 and 13 are prepared for setup and prices. Permissions and service quotas remain open.

## Earlier run and fix

- User run 10 passed 15 tests, Docker smoke, golden predictions, and batch 100.
- Load: 200 requests, concurrency 10, zero errors, mean 130.33 ms, p95 274.54 ms. The local 300 ms target passed.
- The model artifact is unchanged. The serving image is `sha256:689d113ccc3d3b024682d2c6ea632c00d4bc0a07c3f89c86d1596d23b9872d36`.
- User run 11 failed with `TypeError` when subtracting string quota counts. The notebook only showed its generic assertion.
- Quota counts now accept integers and valid integer strings. Invalid counts stay unknown and add a failed check. The notebook also shows Python failures before stopping.
- Three regression tests passed. A separate assistant read-only Azure check completed with no failed checks after the fix. It did not replace the user's notebook output or write `azure-preflight.json`.
- That check listed southeastasia for all seven service types. Microsoft.App was NotRegistered; the other six providers were Registered. Remaining VM quota was 6 total cores and 4 DSv2 cores. Only the ml CLI extension was installed.
- This does not establish Azure ML or Container Apps quotas, deployment permissions, prices, or paid-work readiness.
- The failed notebook and earlier script are preserved in `reports/history/11-error/`. The corrected user report is now available; save the latest notebook output.
