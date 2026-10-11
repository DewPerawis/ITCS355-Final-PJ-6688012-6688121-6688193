import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from cloudlayer.finish_serve import app_body
from scripts.train_selected import sha, train
from src.data import FEATURES
from src.train import make_pipeline


class FinishTests(unittest.TestCase):
    def test_app_has_bounded_scale_https_and_managed_pull(self):
        cloud = SimpleNamespace(region="centralindia", tags={"project": "test"}, host="registry.test",
                                base="https://management.azure.com/subscriptions/test/resourceGroups/project/providers/",
                                environment="environment")
        body = app_body(cloud, "registry.test/model@sha256:abc", "/identity/test")
        self.assertEqual(body["properties"]["template"]["scale"]["maxReplicas"], 1)
        self.assertEqual(body["properties"]["template"]["scale"]["minReplicas"], 0)
        self.assertNotIn("revisionSuffix", body["properties"]["template"])
        self.assertFalse(body["properties"]["configuration"]["ingress"]["allowInsecure"])
        self.assertEqual(body["properties"]["configuration"]["registries"][0]["identity"], "/identity/test")

    def test_training_refits_and_preserves_verified_canonical_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frame = pd.DataFrame(np.random.default_rng(42).uniform(0, 5, (32, 24)), columns=FEATURES)
            frame["profile_hash"] = [str(i) for i in range(len(frame))]
            frame["split"] = "train"
            path = root / "profiles.csv"
            frame.to_csv(path, index=False)
            # CSV parsing is part of the reproducibility contract.
            values = pd.read_csv(path)[FEATURES]
            with threadpool_limits(limits=1):
                pipeline = make_pipeline("keep_zero", 2, 42).fit(values)
                labels = pipeline.predict(values)
                distances = pipeline.named_steps["model"].transform(pipeline[:-1].transform(values))
            bundle = {"pipeline": pipeline, "thresholds": {i: float(np.quantile(distances[labels == i, i], .95)) for i in range(2)}}
            joblib.dump(bundle, root / "bundle.joblib")
            (root / "bundle-manifest.json").write_text(json.dumps({"artifact_sha256": sha(root / "bundle.joblib"),
                "features": FEATURES, "model_version": "test"}))
            (root / "prepared-data.json").write_text(json.dumps({"files": {"data/processed/profiles.csv": sha(path)}}))
            (root / "selection.json").write_text(json.dumps({"packages": {}, "distance_quantile": .95}))
            (root / "golden-profiles.json").write_text("{}")
            report = train(path, root, root / "output")
            self.assertTrue(report["fresh_fit_equivalent"])
            self.assertEqual(sha(root / "output/bundle.joblib"), sha(root / "bundle.joblib"))
            path.write_text("changed")
            with self.assertRaises(ValueError):
                train(path, root, root / "output")




class AzureOutputTests(unittest.TestCase):
    def test_success_without_json_output_is_allowed(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from cloudlayer import platform_preview
        with patch("cloudlayer.platform_preview.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
            self.assertIsNone(platform_preview.azure(["group", "delete"], {}))


class DriftTests(unittest.TestCase):
    def test_controlled_shift_is_detected_without_changing_recent(self):
        from monitoring.drift import evaluate, score
        rng = np.random.default_rng(7)
        train = rng.uniform(0, 3, (800, 24))
        recent = rng.uniform(0, 3, (300, 24))
        original = recent.copy()
        result = evaluate(train, recent, rounds=20)
        self.assertTrue(result["injected_detected"])
        np.testing.assert_array_equal(recent, original)
        with self.assertRaises(ValueError):
            score(train[:100], recent[:200])


class RecoveryTests(unittest.TestCase):
    def test_ready_old_mapping_does_not_count_as_recovered(self):
        from unittest.mock import Mock, patch
        from cloudlayer.finish_serve import wait_canary
        cloud = Mock()
        cloud.get.return_value = {"properties": {"provisioningState": "Succeeded",
            "configuration": {"ingress": {"fqdn": "staging.test"}}}}
        responses = [(200, {"model_version": "test"}, 1),
                     (503, {"detail": "Semantic canary failed."}, 1),
                     (200, {"model_version": "test"}, 1),
                     (200, {"passed": True, "model_version": "test"}, 1),
                     (200, {"model_version": "test"}, 1),
                     (200, {"passed": True, "model_version": "test"}, 1)]
        with patch("cloudlayer.finish_serve.http_call", side_effect=responses) as request, patch("cloudlayer.finish_serve.time.sleep"):
            self.assertEqual(wait_canary(cloud, "failure-test", 200, "test"), ("https://staging.test", 200))
        self.assertEqual(request.call_count, 6)

    def test_generic_503_is_not_semantic_failure_evidence(self):
        from unittest.mock import Mock, patch
        from cloudlayer.finish_serve import wait_canary
        cloud = Mock()
        cloud.get.return_value = {"properties": {"provisioningState": "Succeeded",
            "configuration": {"ingress": {"fqdn": "staging.test"}}}}
        with patch("cloudlayer.finish_serve.http_call", side_effect=[(200, {"model_version": "test"}, 1),
                   (503, {"detail": "Model is not ready."}, 1)]), patch("cloudlayer.finish_serve.time.monotonic", side_effect=[0, 0, 181]), patch("cloudlayer.finish_serve.time.sleep"):
            with self.assertRaises(RuntimeError):
                wait_canary(cloud, "failure-test", 503, "test")

    def test_restart_requests_start_even_when_stop_fails(self):
        from unittest.mock import Mock
        from cloudlayer.finish_serve import restart_staging
        cloud = Mock()
        cloud.plan = {"suffix": "test"}
        cloud.tags = {"project": "test"}
        cloud.base = "https://management.test/"
        cloud.get.return_value = {"tags": {"project": "test"}}
        cloud.az.side_effect = [RuntimeError("stop failed"), None]
        with self.assertRaises(RuntimeError):
            restart_staging(cloud, "failure-test")
        self.assertEqual(cloud.az.call_count, 2)
        self.assertIn("/start?", cloud.az.call_args.args[0][-1])

    def test_restart_rejects_main_app(self):
        from unittest.mock import Mock
        from cloudlayer.finish_serve import restart_staging
        cloud = Mock()
        cloud.plan = {"suffix": "test"}
        with self.assertRaises(ValueError):
            restart_staging(cloud, "travel-style-test")
        cloud.az.assert_not_called()


class AlertEvidenceTests(unittest.TestCase):
    def test_full_rule_id_and_named_rule_match_owned_alerts(self):
        from cloudlayer.finish_monitor import matching_alerts
        rule_id = "/subscriptions/test/resourceGroups/project/providers/Microsoft.Insights/scheduledQueryRules/mlop-semantic-failure"
        def row(rule, group, condition):
            return {"properties": {"essentials": {"alertRule": rule, "targetResourceGroup": group, "monitorCondition": condition}}}
        values = [row(rule_id.lower(), "PROJECT", "Fired"),
                  row("MLOP semantic canary failure", "project", "Resolved"),
                  row(rule_id.replace("/project/", "/other/"), "other", "Fired"),
                  row("mlop-semantic-failure", "other", "Fired"),
                  row(rule_id, "project", None)]
        self.assertEqual(len(matching_alerts(values, "project", rule_id)), 2)


class CIRoleTests(unittest.TestCase):
    def test_uses_actual_returned_role_id_and_rejects_extra_permissions(self):
        from cloudlayer.finish_ci import checked_role_id
        role_id = "11111111-2222-4333-8444-555555555555"
        scope = "/subscriptions/test/resourceGroups/project"
        value = {"name": role_id, "id": "/subscriptions/test/providers/Microsoft.Authorization/roleDefinitions/" + role_id,
                 "roleName": "CI test", "roleType": "CustomRole", "assignableScopes": [scope],
                 "permissions": [{"actions": ["app/read"], "notActions": [], "dataActions": [], "notDataActions": []}]}
        self.assertEqual(checked_role_id(value, "CI test", scope, ["app/read"]), role_id)
        value["permissions"][0]["actions"].append("*")
        with self.assertRaises(ValueError):
            checked_role_id(value, "CI test", scope, ["app/read"])

    def test_only_role_propagation_error_is_retried(self):
        from unittest.mock import Mock, patch
        from cloudlayer.finish_ci import assign_custom_role
        cloud = Mock()
        cloud.role.side_effect = [RuntimeError("RoleDefinitionDoesNotExist"), None]
        with patch("cloudlayer.finish_ci.time.sleep"):
            assign_custom_role(cloud, "principal", "scope", "role")
        self.assertEqual(cloud.role.call_count, 2)
        cloud.role.reset_mock()
        cloud.role.side_effect = RuntimeError("AuthorizationFailed")
        with self.assertRaises(RuntimeError):
            assign_custom_role(cloud, "principal", "scope", "role")
        self.assertEqual(cloud.role.call_count, 1)


class RegistryVersionTests(unittest.TestCase):
    def test_numeric_versions_and_repeat_registration(self):
        from cloudlayer.finish_build import registry_version
        self.assertEqual(registry_version([], "train-test", "hash", "code"), ("1", False))
        existing = [{"name": "1", "properties": {"tags": {"training_job": "train-test",
                    "canonical_sha256": "hash", "source_sha256": "code"}}}]
        self.assertEqual(registry_version(existing, "train-test", "hash", "code"), ("1", True))
        self.assertEqual(registry_version(existing, "train-next", "hash", "code"), ("2", False))
        with self.assertRaises(ValueError):
            registry_version(existing, "train-test", "changed", "code")
        with self.assertRaises(ValueError):
            registry_version([{"name": "20261011-164656"}], "train-test", "hash", "code")


class GitHubEvidenceTests(unittest.TestCase):
    def test_oidc_subject_matches_verified_ids_and_staging(self):
        from cloudlayer.finish_ci import REPOSITORY, staging_subject
        repository = {"full_name": REPOSITORY, "id": 456, "owner": {"login": REPOSITORY.split("/")[0], "id": 123}}
        owner, name = REPOSITORY.split("/")
        for immutable in [False, True]:
            prefix = f"repo:{owner}@123/{name}@456" if immutable else "repo:" + REPOSITORY
            settings = {"use_default": True, "use_immutable_subject": immutable, "sub_claim_prefix": prefix}
            self.assertEqual(staging_subject(repository, settings), prefix + ":environment:staging")
            with self.assertRaises(ValueError):
                staging_subject(repository, dict(settings, sub_claim_prefix=prefix + "-other"))
            with self.assertRaises(ValueError):
                staging_subject(repository, dict(settings, use_default=False))

    def test_colored_json_is_read_without_changing_parent_environment(self):
        import os
        from cloudlayer.finish_ci import github_json
        output = '\ufeff\x1b[1;38m{\x1b[m"total_count":0,"environments":[]}'
        with patch.dict(os.environ, {"GH_FORCE_TTY": "80", "CLICOLOR_FORCE": "1", "GH_TOKEN": "test-token"}):
            with patch("cloudlayer.finish_ci.command", return_value=output) as call:
                self.assertEqual(github_json(["gh", "api", "test"], "test"), {"total_count": 0, "environments": []})
            env = call.call_args.kwargs["env"]
            self.assertNotIn("GH_FORCE_TTY", env)
            self.assertEqual(env["CLICOLOR_FORCE"], "0")
            self.assertEqual(env["GH_TOKEN"], "test-token")
            self.assertEqual(os.environ["GH_FORCE_TTY"], "80")

    def test_invalid_response_is_not_accepted_as_success(self):
        from cloudlayer.finish_ci import github_json
        for output in ["", "Proxy error: private-value", 'HTTP/1.1 200 OK\n{"total_count":0}', '[]']:
            with self.subTest(output=output), patch("cloudlayer.finish_ci.command", return_value=output):
                with self.assertRaises(RuntimeError) as error:
                    github_json(["gh", "api", "test"], "github-settings")
                self.assertNotIn("private-value", str(error.exception))

    def test_missing_workflow_is_pending_without_querying_runs(self):
        from unittest.mock import patch
        from cloudlayer.finish_ci import check_runs
        report = {}
        with patch("cloudlayer.finish_ci.command", side_effect=["owner/repo", '{"total_count":0,"workflows":[]}']) as call:
            check_runs(report)
        self.assertFalse(report["ci_evidence_ready"])
        self.assertTrue(report["pending"])
        self.assertFalse(report["workflow_published"])
        self.assertEqual(call.call_count, 2)

    def test_github_setup_rejects_unknown_local_values(self):
        from scripts.github_setup import check_values
        with self.assertRaises(ValueError):
            check_values({"PASSWORD": "do-not-publish"})


if __name__ == "__main__":
    unittest.main()
