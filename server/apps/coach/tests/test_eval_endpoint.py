"""
Endpoint tests for the coach eval harness API (POST /api/v1/eval/run).

run_phase_eval is mocked throughout — these tests cover auth, the env gate,
request wiring, and error mapping, NOT the (LLM-driven) eval itself.
"""

from unittest.mock import patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.coach.eval.harness import EvalError
from apps.test_scenario.models import TestScenario
from apps.users.models import User

URL = "/api/v1/eval/run"
FAKE_REPORT = {"status": "ok", "scenario": "cold get_to_know_you", "quality": {"score": 5}}


@override_settings(EVAL_HARNESS_ENABLED="true")
class EvalEndpointTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )

    @patch("apps.coach.views.eval_view_set.run_phase_eval", return_value=FAKE_REPORT)
    def test_runs_and_returns_report(self, mock_run):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(URL, {"persona": "casey"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), FAKE_REPORT)
        # Serializer defaults are forwarded.
        kwargs = mock_run.call_args.kwargs
        self.assertEqual(kwargs["persona_id"], "casey")
        self.assertEqual(kwargs["max_turns"], 20)
        self.assertIsNone(kwargs["scenario_name"])

    @patch("apps.coach.views.eval_view_set.run_phase_eval", return_value=FAKE_REPORT)
    def test_forwards_optional_args(self, mock_run):
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            URL,
            {"from_scenario": "S1", "prompt_version": 5, "checks": ["x"], "max_turns": 8},
            format="json",
        )
        kwargs = mock_run.call_args.kwargs
        self.assertEqual(kwargs["scenario_name"], "S1")
        self.assertEqual(kwargs["prompt_version"], 5)
        self.assertEqual(kwargs["checks"], ["x"])
        self.assertEqual(kwargs["max_turns"], 8)

    def test_non_admin_rejected(self):
        regular = User.objects.create_user(email="r@example.com", password="TestPass1!")
        self.client.force_authenticate(user=regular)
        resp = self.client.post(URL, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "apps.coach.views.eval_view_set.run_phase_eval",
        side_effect=TestScenario.DoesNotExist,
    )
    def test_unknown_scenario_404(self, _mock):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(URL, {"from_scenario": "nope"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch(
        "apps.coach.views.eval_view_set.run_phase_eval",
        side_effect=EvalError("No active coach prompt for phase 'x'"),
    )
    def test_eval_error_400(self, _mock):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(URL, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No active coach prompt", resp.json()["detail"])

    def test_max_turns_over_cap_rejected(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(URL, {"max_turns": 999}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class EvalEndpointGateTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin2@example.com", password="TestPass1!", is_staff=True
        )

    @override_settings(EVAL_HARNESS_ENABLED="false")
    @patch("apps.coach.views.eval_view_set.run_phase_eval", return_value=FAKE_REPORT)
    def test_disabled_returns_403_and_skips_eval(self, mock_run):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(URL, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        mock_run.assert_not_called()
