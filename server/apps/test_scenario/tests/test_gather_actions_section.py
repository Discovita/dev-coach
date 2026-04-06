"""
Tests for gather_actions_section function.
"""

from django.test import TestCase

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.test_scenario.utils import gather_actions_section
from apps.users.models import User


class TestGatherActionsSection(TestCase):
    """gather_actions_section tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="gather_act@example.com", password="testpass"
        )
        # Action requires a linked coach ChatMessage (NOT NULL FK)
        self.coach_msg = ChatMessage.objects.create(
            user=self.user, role="coach", content="A message"
        )

    def _make_action(self, user=None, parameters=None, **kwargs):
        """Helper to create an Action with the required coach_message."""
        return Action.objects.create(
            user=user or self.user,
            action_type="CREATE_IDENTITY",
            parameters=parameters if parameters is not None else {},
            coach_message=self.coach_msg,
            **kwargs,
        )

    # ==================== Empty case ====================

    def test_returns_empty_list_when_no_actions(self):
        """Should return an empty list when the user has no actions."""
        result = gather_actions_section(self.user)
        self.assertEqual(result, [])

    # ==================== Basic output ====================

    def test_entry_contains_action_type_and_parameters(self):
        """Each entry should always contain action_type and parameters."""
        self._make_action(parameters={"name": "Explorer"})
        result = gather_actions_section(self.user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["action_type"], "CREATE_IDENTITY")
        self.assertEqual(result[0]["parameters"], {"name": "Explorer"})

    def test_result_summary_included_when_present(self):
        """Should include result_summary when non-empty."""
        self._make_action(result_summary="Identity created.")
        result = gather_actions_section(self.user)
        self.assertIn("result_summary", result[0])
        self.assertEqual(result[0]["result_summary"], "Identity created.")

    def test_result_summary_omitted_when_empty(self):
        """Should omit result_summary when it is an empty string or None."""
        self._make_action(result_summary=None)
        result = gather_actions_section(self.user)
        self.assertNotIn("result_summary", result[0])

    def test_timestamp_always_included(self):
        """Should always include timestamp (auto_now_add on Action)."""
        self._make_action()
        result = gather_actions_section(self.user)
        self.assertIn("timestamp", result[0])
        self.assertIsInstance(result[0]["timestamp"], str)

    def test_coach_message_id_included_when_linked(self):
        """Should include original_coach_message_id when action has a coach_message."""
        self._make_action()
        result = gather_actions_section(self.user)
        self.assertIn("original_coach_message_id", result[0])
        self.assertEqual(result[0]["original_coach_message_id"], str(self.coach_msg.id))

    def test_does_not_return_other_users_actions(self):
        """Should only return actions for the specified user."""
        other = User.objects.create_user(
            email="other_gather_act@example.com", password="testpass"
        )
        other_msg = ChatMessage.objects.create(
            user=other, role="coach", content="Other msg"
        )
        Action.objects.create(
            user=other,
            action_type="CREATE_IDENTITY",
            parameters={},
            coach_message=other_msg,
        )
        result = gather_actions_section(self.user)
        self.assertEqual(result, [])
