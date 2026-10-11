import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from cloudlayer.finish_monitor import log_query
from cloudlayer.session import ROOT, Session, command, read, write


def optional(name):
    return read("reports/" + name) if (ROOT / "reports" / name).exists() else {}


def model_card():
    model = read("reports/bundle-manifest.json")
    source = read("reports/data-source.json")
    text = f'''# Model card: Travel Style Segmentation

**Version:** {model['model_version']} · **Model:** K-Means, k=5 · **Owner:** ITCS355 team 6688012/6688121/6688193.

**Use.** Group 24-category travel-rating profiles for a coursework preference service. Segment names are provisional. This is not a personality test or a high-stakes recommendation system.

**Data.** UCI Travel Review Ratings, DOI {source['doi']}, CC BY 4.0. Raw SHA-256: {model['raw_sha256']}. The audit accepted 5,454 rows and quarantined two malformed rows. Identical profiles stay in one split: 3,817 training, 817 validation, 820 test. User IDs are excluded from model features.

**Training.** Keep zeros as supplied, then median imputation, standard scaling, and K-Means with seed 42 and n_init=10. Preprocessing is fitted on training data. Validation chooses the configuration; the test set is reserved. Azure training re-fits the selected model and checks equivalence before exporting the tested canonical bundle.

**Observed local quality.** Validation silhouette 0.1448; seed stability ARI 1.0. Held-out silhouette {model['test_metrics']['silhouette']:.4f}, Davies–Bouldin {model['test_metrics']['davies_bouldin']:.4f}. Cluster sizes: 281, 86, 278, 35, 140. GMM validation silhouette was 0.0957. These are clustering metrics, not prediction accuracy.

**Input/output.** Exactly 24 finite numeric ratings in [0,5], batch size 1–100. Invalid input returns 422. A profile above its cluster's training-distance 95th percentile is marked uncertain and returns a null segment with HTTP 200. Distance is not a probability.

**Limits.** The meaning of zeros is unknown. The dataset may not represent current users. Segment names need domain review. There is no causal claim, calibrated confidence, or fairness result. Input drift alone does not prove concept drift.

**Operations.** The bundle includes preprocessing, feature order, centers, mapping, thresholds, and versions. Hash and golden checks gate startup. A semantic canary detects mapping regressions; the staging failure is restored and covered by a regression test. Logs contain derived counts, status, latency, and model version, not full profiles.

**Lineage.** Bundle SHA-256: {model['artifact_sha256']}. Cloud registry evidence: reports/finish-training-registry.json. Latest CI image and deployment: reports/ci-deploy-result.json. Initial build/deploy: reports/finish-assets.json and reports/finish-deploy.json. Only completed runs support those claims.
'''
    (ROOT / "docs/MODEL_CARD.md").write_text(text)


def delivery(report):
    model_card()
    audit = command([sys.executable, "scripts/portability_audit.py"], "portability-audit")
    report["portability_passed"] = "PASSED" in audit
    plan = read("reports/azure-cost-plan.json")
    cost = {"basis": "Short-demo planning estimate; not the actual bill", "planned_total_thb": plan["planned_total_thb"],
            "planned_predictions": plan["assumptions"]["app_requests"],
            "planned_thb_per_1000_predictions": round(plan["planned_total_thb"] / plan["assumptions"]["app_requests"] * 1000, 2),
            "actual_cost_per_1000_predictions": None, "actual_cost_ready": False,
            "limits": ["Planning treats each request as one prediction and includes the stated reserve.",
                       "Do not claim the planned figure as the actual bill or a spending cap."]}
    with Session() as cloud:
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(read("reports/azure-platform-deploy.json")["checked_at"]).astimezone(timezone.utc)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        body = {"type": "ActualCost", "timeframe": "Custom", "timePeriod": {"from": start.isoformat(), "to": now.isoformat()},
                "dataset": {"granularity": "None", "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
                            "filter": {"dimensions": {"name": "ResourceGroupName", "operator": "In", "values": [cloud.group]}}}}
        file = ROOT / "tmp/cost-query.json"
        file.write_text(json.dumps(body))
        try:
            page = cloud.az(["rest", "--method", "post", "--url",
                            f'https://management.azure.com/subscriptions/{cloud.account["id"]}/providers/Microsoft.CostManagement/query?api-version=2025-03-01',
                            "--body", "@" + str(file)])
            write("reports/azure-billing-query.json", page.get("properties", {}))
            values = page.get("properties", {})
            names = [c["name"] for c in values.get("columns", [])]
            rows = values.get("rows", [])
            if not values.get("nextLink") and rows and "Currency" in names:
                currencies = {r[names.index("Currency")] for r in rows}
                cost_columns = [i for i, name in enumerate(names) if name in {"PreTaxCost", "totalCost", "Cost"}]
                if len(currencies) == 1 and len(cost_columns) == 1:
                    reported = sum(float(r[cost_columns[0]]) for r in rows)
                    query = ("ContainerAppConsoleLogs_CL | where TimeGenerated between (datetime(" + start.isoformat() + ") .. datetime(" + now.isoformat() + ")) "
                             f"| where ContainerAppName_s in ('{cloud.app}', 'failure-{cloud.plan['suffix']}') "
                             "| extend j=parse_json(Log_s) | where tostring(j.event)=='prediction_batch' "
                             "| summarize Predictions=sum(toint(j.count))")
                    logs = log_query(cloud, query, start.isoformat() + "/" + now.isoformat())
                    tables = logs.get("tables", [])
                    count = int(tables[0]["rows"][0][0] or 0) if tables and tables[0].get("rows") else 0
                    cost.update(reported_pretax_cost=reported, billing_currency=next(iter(currencies)),
                                observed_predictions=count, billing_from_utc=start.isoformat(), billing_to_utc=now.isoformat(),
                                actual_cost_ready=reported > 0 and count > 0,
                                actual_cost_per_1000_predictions=reported / count * 1000 if reported > 0 and count > 0 else None,
                                actual_basis="Project Resource Group reported PreTaxCost divided by observed valid API profile count over the same deployment-to-query UTC window.",
                                actual_limits="Billing and telemetry may lag. Reported cost may include only part of the usage so far. This is provisional; free grants, billing currency and missing logs must be reviewed. It is not a final invoice or the before-credit planning budget.")
        except RuntimeError as error:
            cost["billing_pending_reason"] = str(error)
    write("reports/cost-per-1000.json", cost)
    checks = {
        "versioned_data_remote": optional("finish-assets.json").get("dvc_fresh_pull_passed") is True,
        "managed_training_registry": optional("finish-training-registry.json").get("registry_ready") is True,
        "deployed_inference": optional("finish-deploy.json").get("api_ready") is True,
        "ci_cd_evidence": optional("finish-ci-evidence.json").get("ci_evidence_ready") is True,
        "dashboard": optional("finish-monitor.json").get("dashboard_created") is True,
        "actual_alert_event": optional("finish-alert.json").get("alert_fired") is True,
        "failure_and_recovery": optional("finish-failure.json").get("failure_demo_passed") is True,
        "controlled_input_drift_evidence": optional("input-drift.json").get("verified") is True,
        "cost_documented": True, "actual_cost_available": cost["actual_cost_ready"],
        "model_card": (ROOT / "docs/MODEL_CARD.md").exists(), "portability": report["portability_passed"]}
    report.update(checks=checks, open_items=[name for name, passed in checks.items() if not passed],
                  required_evidence_complete=all(checks.values()),
                  latency_target_met=optional("finish-deploy.json").get("latency_target_met", False),
                  cold_start_measured=optional("finish-cold.json").get("cold_start_measured", False),
                  cleanup_verified=False)
    lines = ["# Delivery status", "", "Checked: " + report["checked_at"], "", "| Evidence | Status |", "|---|---|"]
    lines += [f"| {name} | {'Verified' if value else 'Pending'} |" for name, value in checks.items()]
    lines += ["", "Latency and cold start are reported separately. Cleanup must be run and verified after evidence is saved.",
              "", "Do not mark the project complete while required evidence is pending."]
    (ROOT / "docs/DELIVERY_STATUS.md").write_text("\n".join(lines) + "\n")
