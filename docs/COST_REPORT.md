# Cost report

## Estimate

The short-demo plan totals 88.89 THB before credits. It assumes 10,000 requests with one prediction each, two registry days, one DS2 v2 training hour, two active app hours, and a 60 THB reserve. The planning exchange rate is 40 THB/USD, not the billing rate.

Estimated cost per 1,000 predictions = 88.89 / 10,000 * 1,000 = 8.89 THB.

## Actual cost

The latest query returned a reported pre-tax cost of 0.0012035014 USD. Logs recorded 841 valid profiles in the same query window. Provisional reported cost per 1,000 predictions = 0.0012035014 / 841 * 1,000 = 0.00143104 USD. See reports/cost-per-1000.json for the exact window and provider response.

This small reported amount may include only part of the usage so far. It is not a final invoice, a before-credit cost, or proof that the total demo cost stays within 150 THB. Do not convert it with the planning exchange rate and call that the billed THB amount. Recheck after billing settles and after cleanup.

Actual cost per 1,000 predictions = reported project cost / observed valid profile count in the same UTC window * 1,000. Show the reported currency. Billing and logs can lag, so the figure is provisional.

## Applied limits

The app uses minReplicas=0 and maxReplicas=1. Training uses zero idle nodes and at most one node. ACR, storage, and monitoring can still cost money while the app is idle. Cleanup removes the project group after evidence and the demo are finished.

The serving changes reduced measured local p95 from 496.01 ms to 274.54 ms. This is a latency result; we have not measured a billing saving from it. See reports/azure-cost-plan.json and reports/cost-per-1000.json for the calculation and current status.
