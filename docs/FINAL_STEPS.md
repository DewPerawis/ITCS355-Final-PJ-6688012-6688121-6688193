# Final steps

1. In Notebook 22, run setup if needed. Close API tabs and stop request loops. Run the cold-start cell only. Check cold_start_measured=true. It reads revision and replica state, then sends one readiness request; it does not redeploy. A pending result means there is still a replica. Keep the cold result even if it is slow.
2. Run the delivery cell. Inspect open_items. Billing may still be pending; retry delivery later when billing has data. Do not replace the estimate with a claimed actual bill.
3. Save dashboard and actual-alert screenshots from Azure Portal. Open Resource groups > rg-mlop-pj-492ea24d. Open the Log Analytics workspace and Workbooks > MLOP Travel Style for the dashboard. For the fired/resolved alert, open Azure Monitor > Alerts and use the time in reports/finish-alert.json. Hide private account details.
4. The deck is output/presentation/6688012_6688121_6688193_Presentation.pptx. Follow docs/PRESENTATION.md for the 8-minute plan and live API cell; keep 5 minutes for questions. Explain the missed cloud latency target and offline drift scope honestly. The one-page model card is ready in output/pdf/MODEL_CARD.pdf.
5. Final source commit 9fea51a has normal and demo_failure workflow evidence. Review docs and reports before submitting. Changed source needs new runs; documentation-only updates can keep the same tested commit. Keep private files out.
6. After saving evidence and finishing the live demo, delete the project resource group. This removes all project cloud data, models, images, API, training, and monitoring. Run the following command from the project root in WSL only when you are ready for that deletion:

```bash
python -m cloudlayer.cleanup --confirm-group rg-mlop-pj-492ea24d
```

Check reports/cleanup.json for cleanup_verified=true. Keep local evidence and the agreed data access plan for the reviewer. The reminder is 13 October 2026 at 21:15 Bangkok time, not an automatic deletion.

Before any final documentation push after cleanup, disable the old Test and deploy workflow in GitHub Actions. Its current configuration deploys on every main push, including documentation changes. Keep its historical runs as evidence. A disabled workflow is a deliberate post-demo shutdown, not a new CI result.
