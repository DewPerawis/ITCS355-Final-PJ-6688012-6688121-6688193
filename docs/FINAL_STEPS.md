# Final steps

1. In Notebook 22, run setup if needed. Close API tabs and stop request loops. Run the cold-start cell only. Check cold_start_measured=true. It reads revision and replica state, then sends one readiness request; it does not redeploy. A pending result means there is still a replica. Keep the cold result even if it is slow.
2. Run the delivery cell. Inspect open_items. Billing may still be pending; retry delivery later when billing has data. Do not replace the estimate with a claimed actual bill.
3. Save dashboard and actual-alert screenshots from Azure Portal. Open Resource groups > rg-mlop-pj-492ea24d. Open the Log Analytics workspace and Workbooks > MLOP Travel Style for the dashboard. For the fired/resolved alert, open Azure Monitor > Alerts and use the time in reports/finish-alert.json. Hide private account details.
4. Rehearse the prepared deck in output/presentation/MLOP-PJ_Presentation.pptx. Follow docs/PRESENTATION.md for the 8-minute plan and live API cell; keep 5 minutes for questions. Explain the missed cloud latency target and offline drift scope honestly. The one-page model card is ready in output/pdf/MODEL_CARD.pdf.
5. Review final docs, reports, screenshots, and source. Keep private files out. Publish the reviewed changes, then run normal and demo_failure workflows for that final source commit. Existing CI evidence proves commit 1e0bd12 only. Do not repeatedly create a new commit just to save each CI check result; save the final evidence separately with its tested source commit recorded.
6. After saving evidence and finishing the live demo, delete the project resource group. This removes all project cloud data, models, images, API, training, and monitoring. Run the following command from the project root in WSL only when you are ready for that deletion:

```bash
python -m cloudlayer.cleanup --confirm-group rg-mlop-pj-492ea24d
```

Check reports/cleanup.json for cleanup_verified=true. Keep local evidence and the agreed data access plan for the reviewer. The reminder is 13 October 2026 at 21:15 Bangkok time, not an automatic deletion.
