import argparse
import json
import subprocess
from datetime import datetime, timezone

from cloudlayer.session import write


def run(phase):
    from cloudlayer.finish_build import assets, training_submit, training_finish
    from cloudlayer.finish_serve import deploy, failure, cold, recovery
    from cloudlayer.finish_monitor import monitor, alert_evidence
    from cloudlayer.finish_ci import configure, check_runs
    from cloudlayer.finish_delivery import delivery
    phases = {"assets": assets, "deploy": deploy, "training-submit": training_submit,
              "training-registry": training_finish, "monitor": monitor, "failure": failure,
              "recovery": recovery, "alert": alert_evidence, "ci-setup": configure, "ci-evidence": check_runs, "delivery": delivery, "cold": cold}
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "phase": phase, "errors": []}
    try:
        phases[phase](report)
    except (RuntimeError, ValueError, OSError, KeyError, subprocess.TimeoutExpired) as error:
        report["errors"].append("Command timed out. Check existing resources or jobs before retrying." if isinstance(error, subprocess.TimeoutExpired)
                                else type(error).__name__ + ": " + str(error))
    write("reports/finish-" + phase + ".json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["assets", "deploy", "training-submit", "training-registry", "monitor", "failure",
                                         "recovery", "alert", "ci-setup", "ci-evidence", "delivery", "cold"])
    print(json.dumps(run(parser.parse_args().phase), indent=2))
