"""
Tests for resolve_scenario_coach_message function.
"""

from django.test import TestCase
from django.utils import timezone

from apps.chat_messages.models import ChatMessage
from apps.test_scenario.utils import resolve_scenario_coach_message
from apps.test_scenario.models import TestScenario
from apps.users.models import User


def _make_scenario(name="Resolve Scenario"):
    return TestScenario.objects.create(
        name=name,
        template={"user": {"first_name": "Test", "last_name": "User"}},
    )


class TestResolveScenarioCoachMessage(TestCase):
    """resolve_scenario_coach_message tests."""

    def setUp(self):
        self.scenario = _make_scenario()
        self.user = User.objects.create_user(
            email="resolve_cm@example.com", password="testpass",
            test_scenario=self.scenario,
        )
        self.coach_msg = ChatMessage.objects.create(
            user=self.user,
            test_scenario=self.scenario,
            role="coach",
            content="Coach reply",
            timestamp=timezone.now(),
        )

    # ==================== Fallback (no hints) ====================

    def test_falls_back_to_most_recent_coach_message(self):
        """Should return the most recent coach message when no mapping hints given."""
        action_data = {"action_type": "CREATE_IDENTITY", "parameters": {}}
        result = resolve_scenario_coach_message(
            action_data, {}, self.user, self.scenario, {}
        )
        self.assertEqual(result, self.coach_msg)

    def test_returns_none_when_no_coach_messages_exist(self):
        """Should return None when there are no coach messages at all."""
        ChatMessage.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).delete()
        action_data = {"action_type": "CREATE_IDENTITY", "parameters": {}}
        result = resolve_scenario_coach_message(
            action_data, {}, self.user, self.scenario, {}
        )
        self.assertIsNone(result)

    # ==================== ID-based mapping ====================

    def test_resolves_via_id_based_mapping(self):
        """Should resolve the correct message via original_coach_message_id."""
        original_id = "original-uuid-123"
        ts = self.coach_msg.timestamp.isoformat()
        template = {
            "original_message_mapping": {
                original_id: {
                    "role": "coach",
                    "content": "Coach reply",
                    "timestamp": ts,
                }
            }
        }
        key = f"coach|Coach reply|{ts}"
        original_to_new = {key: self.coach_msg}
        action_data = {
            "action_type": "CREATE_IDENTITY",
            "parameters": {},
            "original_coach_message_id": original_id,
        }
        result = resolve_scenario_coach_message(
            action_data, template, self.user, self.scenario, original_to_new
        )
        self.assertEqual(result, self.coach_msg)

    # ==================== Content-based matching (deprecated) ====================

    def test_resolves_via_content_matching(self):
        """Should fall back to content matching when coach_message_content is provided."""
        action_data = {
            "action_type": "CREATE_IDENTITY",
            "parameters": {},
            "coach_message_content": "Coach reply",
        }
        result = resolve_scenario_coach_message(
            action_data, {}, self.user, self.scenario, {}
        )
        self.assertEqual(result, self.coach_msg)
