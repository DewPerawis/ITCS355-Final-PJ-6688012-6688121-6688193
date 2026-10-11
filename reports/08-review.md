# Notebook 08 review

- Docker build and real HTTP smoke passed for bundle `abfd88e893ca`.
- Golden predictions and batch 100 passed. The 200 load requests had no errors.
- Client mean: 415.50 ms. Client p95: 567.99 ms. The 300 ms target was not met.
- Local startup-to-ready: 4.91 s, including Docker launch and polling.
- The old checker built a new urllib opener inside every request timer. In the installed Python, this also created a default TLS context, even for local HTTP.
- A separate 20-call setup check averaged 44.52 ms per opener. This is evidence of client overhead, not a full explanation of the p95 result.
- The fixed checker reuses one verified TLS context and one opener per client thread. Response checks and the latency target are unchanged.
- `reports/history/08-initial/` keeps the original notebook and reports. Notebook 09 reuses the same image and writes separate reports to `reports/http-recheck/`.
- No corrected Docker p95 result exists yet. Local results do not prove Azure performance.

Reference: [Python urllib documentation](https://docs.python.org/3.13/library/urllib.request.html#urllib.request.build_opener).
