# Cost report

## Estimate

The short-demo plan totals 88.89 THB before credits. It assumes 10,000 requests with one prediction each, two registry days, one DS2 v2 training hour, two active app hours, and a 60 THB reserve. The planning exchange rate is 40 THB/USD, not the billing rate.

Estimated cost per 1,000 predictions = 88.89 / 10,000 * 1,000 = 8.89 THB.

## Latest reported cost - 16 October 2026

A read-only query at 2026-10-16T12:25:27.812860+00:00 returned 1.44540967899556 USD for the project resource group. The same UTC window, starting 11 October at 00:00, contained 2,707 logged valid profiles across the main and failure apps.

Reported cost per 1,000 predictions = 1.44540967899556 / 2,707 * 1,000 = 0.5339525966 USD.

The raw billing and prediction-query responses are in reports/billing-submission-check.json. This includes idle cloud time after the demo. It is a provisional reported amount, not a final invoice or before-credit cost. At this query, the group still contained 13 resources. Cleanup was subsequently verified in reports/cleanup.json. Do not use the earlier demo-period amount as the latest total.

## Earlier demo-period reported cost

The earlier demo-period query returned a reported pre-tax cost of 0.0012035014 USD. Logs recorded 841 valid profiles in the same query window. Provisional reported cost per 1,000 predictions = 0.0012035014 / 841 * 1,000 = 0.00143104 USD. See reports/cost-per-1000.json for the exact window and provider response.

This small reported amount may include only part of the usage so far. It is not a final invoice, a before-credit cost, or proof that the total demo cost stays within 150 THB. Do not convert it with the planning exchange rate and call that the billed THB amount. Recheck after billing settles and after cleanup.

Actual cost per 1,000 predictions = reported project cost / observed valid profile count in the same UTC window * 1,000. Show the reported currency. Billing and logs can lag, so the figure is provisional.

## Applied limits

The app uses minReplicas=0 and maxReplicas=1. Training uses zero idle nodes and at most one node. ACR, storage, and monitoring can still cost money while the app is idle. The project group was removed after evidence and the demo were finished; reports/cleanup.json verifies the deletion.

The serving changes reduced measured local p95 from 496.01 ms to 274.54 ms. This is a latency result; we have not measured a billing saving from it. See reports/azure-cost-plan.json and reports/cost-per-1000.json for the calculation and current status.
