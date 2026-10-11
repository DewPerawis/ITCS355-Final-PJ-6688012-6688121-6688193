import json
from uuid import NAMESPACE_URL, uuid5

from cloudlayer.session import ROOT, Session, read, write
from scripts.http_check import http_call


def log_query(cloud, query, timespan="PT1H"):
    logs = cloud.get("Microsoft.OperationalInsights/workspaces/log-mlop-pj-" + cloud.plan["suffix"], "2023-09-01")
    file = ROOT / "tmp/log-query.json"
    file.write_text(json.dumps({"query": query, "timespan": timespan}))
    return cloud.az(["rest", "--method", "post", "--resource", "https://api.loganalytics.io",
                     "--url", "https://api.loganalytics.azure.com/v1/workspaces/" + logs["properties"]["customerId"] + "/query",
                     "--body", "@" + str(file)])


def queries(app):
    where = f"ContainerAppConsoleLogs_CL | where ContainerAppName_s in ('{app}', 'failure-{app.rsplit('-', 1)[-1]}')"
    return {
        "requests": where + " | extend j=parse_json(Log_s) | where isnotempty(j.path) "
                    "| summarize Requests=count(), Errors=countif(toint(j.status)>=500), "
                    "MeanMs=avg(todouble(j.duration_ms)), P95Ms=percentile(todouble(j.duration_ms),95) "
                    "by bin(TimeGenerated, 1m), Model=tostring(j.model_version)",
        "profiles": where + " | extend j=parse_json(Log_s) | where tostring(j.event)=='prediction_batch' "
                    "| summarize Predictions=sum(toint(j.count)), Uncertain=sum(toint(j.uncertain_count)) by bin(TimeGenerated,1m)",
        "failure": where + " | where Log_s contains 'semantic_canary_failed'"}


def monitor(report):
    deployed = read("reports/finish-deploy.json")
    if deployed["errors"] or not deployed.get("api_ready"):
        raise ValueError("Deploy and check the API first.")
    with Session() as cloud:
        http_call(deployed["url"], "/canary")
        logs = cloud.get("Microsoft.OperationalInsights/workspaces/log-mlop-pj-" + cloud.plan["suffix"], "2023-09-01")
        scope = logs["id"]
        kql = queries(cloud.app)
        telemetry = log_query(cloud, kql["requests"])
        write("reports/azure-telemetry.json", telemetry)
        if not any(t.get("rows") for t in telemetry.get("tables", [])):
            report.update(pending=True, monitor_ready=False,
                          next="Logs have not arrived. Wait a few minutes, then rerun this cell. Do not run the failure demo yet.")
            return
        serialized = {"version": "Notebook/1.0", "isLocked": False, "fallbackResourceIds": [scope], "items": [
            {"type": 1, "name": "intro", "content": {"json": "# Travel Style API\nServer latency, requests, errors, model version, and uncertainty. Client latency is reported separately."}},
            *[{"type": 3, "name": key, "content": {"version": "KqlItem/1.0", "query": query,
               "size": 0, "queryType": 0, "resourceType": "microsoft.operationalinsights/workspaces",
               "crossComponentResources": [scope], "visualization": "table", "title": key}}
              for key, query in kql.items()]]}
        name = str(uuid5(NAMESPACE_URL, scope + "/mlop-dashboard"))
        cloud.put("Microsoft.Insights/workbooks/" + name, "2022-04-01", {
            "location": cloud.region, "kind": "shared", "tags": cloud.tags,
            "properties": {"displayName": "MLOP Travel Style", "category": "workbook", "sourceId": scope,
                           "serializedData": json.dumps(serialized)}})
        actions = []
        email = (ROOT / "tmp/alert-email.txt").read_text().strip() if (ROOT / "tmp/alert-email.txt").exists() else ""
        if email:
            if "@" not in email or "\n" in email:
                raise ValueError("Enter one valid alert email address.")
            group = cloud.put("Microsoft.Insights/actionGroups/mlop-notify", "2023-01-01", {
                "location": "global", "tags": cloud.tags, "properties": {"groupShortName": "MLOP", "enabled": True,
                    "emailReceivers": [{"name": "owner", "emailAddress": email, "useCommonAlertSchema": True}]}})
            actions = [group["id"]]
        alert = cloud.put("Microsoft.Insights/scheduledQueryRules/mlop-semantic-failure", "2023-12-01", {
            "location": cloud.region, "kind": "LogAlert", "tags": cloud.tags,
            "properties": {"displayName": "MLOP semantic canary failure", "description": "A staging mapping regression was detected.",
                "enabled": True, "severity": 2, "evaluationFrequency": "PT1M", "windowSize": "PT15M",
                "scopes": [scope], "autoMitigate": True,
                "criteria": {"allOf": [{"query": kql["failure"], "timeAggregation": "Count",
                    "operator": "GreaterThan", "threshold": 0,
                    "failingPeriods": {"numberOfEvaluationPeriods": 1, "minFailingPeriodsToAlert": 1}}]},
                "actions": {"actionGroups": actions}}})
        report.update(monitor_ready=True, dashboard_created=True, dashboard_name="MLOP Travel Style",
                      alert_created=alert["properties"].get("enabled") is True,
                      email_notifications_configured=bool(email),
                      next="Run the failure cell, then refresh evidence to confirm an actual fired alert.")
        write("monitoring/queries.json", kql)


def matching_alerts(values, group, rule_id):
    matches = []
    for value in values:
        item = value.get("properties", {}).get("essentials", {})
        rule = str(item.get("alertRule") or "").lower()
        target_group = str(item.get("targetResourceGroup") or "").lower()
        exact_id = rule == rule_id.lower()
        named_rule = rule in {"mlop-semantic-failure", "mlop semantic canary failure"}
        owned_rule = (exact_id and target_group in {"", group.lower()}) or (named_rule and target_group == group.lower())
        if owned_rule and item.get("monitorCondition") in {"Fired", "Resolved"}:
            matches.append({key: item.get(key) for key in ["alertRule", "monitorCondition", "alertState", "startDateTime", "lastModifiedDateTime"]})
    return matches


def alert_evidence(report):
    with Session() as cloud:
        url = f'https://management.azure.com/subscriptions/{cloud.account["id"]}/providers/Microsoft.AlertsManagement/alerts?api-version=2019-03-01&timeRange=1d'
        page = cloud.az(["rest", "--method", "get", "--url", url])
        if page.get("nextLink"):
            raise ValueError("Alert results need pagination review.")
        rule_id = (cloud.base + "Microsoft.Insights/scheduledQueryRules/mlop-semantic-failure").replace("https://management.azure.com", "")
        matches = matching_alerts(page.get("value", []), cloud.group, rule_id)
        report.update(alerts=matches, alert_fired=bool(matches), pending=not bool(matches),
                      next="Actual alert evidence found. Save the alert screenshot and continue to CI/CD." if matches else
                           "An actual alert event is required. Rerun after log ingestion and alert evaluation if pending.")
        write("reports/azure-telemetry.json", log_query(cloud, queries(cloud.app)["requests"]))
