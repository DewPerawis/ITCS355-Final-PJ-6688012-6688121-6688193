# Presentation

Open `output/presentation/6688012_6688121_6688193_Presentation.pptx`. It has 15 slides, short speaker notes, and an 8-minute plan. Keep 5 more minutes for questions. The PDF is in `output/presentation/6688012_6688121_6688193_Presentation.pdf`.

| Slides | Topic | Time |
|---|---|---|
| 1-2 | Team and problem | 60 seconds |
| 3-5 | Architecture, data, registry | 90 seconds |
| 6 | Live API demo | 90 seconds |
| 7-9 | CI, latency, monitoring | 85 seconds |
| 10-12 | Failure, drift, cost | 95 seconds |
| 13-15 | Next week, references, questions | 60 seconds |

## Live demo

Open `output/presentation/LIVE_DEMO.ipynb` in VS Code WSL with the MLOP-PJ kernel. Read section 7 of `output/presentation/PROJECT_SUMMARY_TH.md` for the full Thai guide.

After reopening the laptop or restarting the kernel:

1. Run A with `MODE = "cloud"`, then B. Wait for READY FOR DEMO.
2. On stage, run C (input), D (prediction), E (expected 422), and F (batch 100). The output cards call the real API and show the mode.
3. Use G for saved CI links and H for the saved staging incident. I accepts modified input during Q&A.
4. Use J to stop the local demo process. Cloud cleanup is a separate final step.

Cloud mode needs internet and existing Azure resources, but no local server, Docker, Azure login or retraining. Local fallback is explicit: change MODE to local, then rerun A/B. It needs the existing bundle and matching API packages; B starts the local server. Keep the kernel open while presenting.

Do not run all cells on stage: that includes preparation, optional inputs and the stop cell. Collapse code and read the result cards. Local results and saved evidence must be labelled honestly.

## Evidence and limits

The slides use saved project reports and a real API smoke check. Graphs are drawn from those reports; they are not Portal screenshots. Sources and figure paths are in `output/presentation/slide_sources.json`.

- CI evidence covers source commit `9fea51a`. Later documentation and evidence commits keep this proof valid only while CI inputs stay unchanged.
- Warm cloud p95 missed 300 ms. Cold start is one 3.82-second request, not a percentile.
- Input drift is an offline controlled shift. Logged application latency and client HTTPS latency are different measures.
- Keep the planning estimate separate from the provisional reported cost. The reported row may not include all usage yet.
- The dashboard export is in `reports/dashboard-workbook.json`. Portal screenshots are useful extra evidence. The reminder is 13 October 2026, 21:15 Bangkok; it does not delete resources.

The deck keeps the supplied template's backgrounds, decoration, fonts, and Mahidol logo. Old research text, other institutions, speaker notes, and embedded objects were removed from the new file. The original `example.pptx` was kept unchanged.
