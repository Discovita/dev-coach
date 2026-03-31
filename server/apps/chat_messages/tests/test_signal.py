"""
Tests for the trigger_sentinel_on_user_message signal.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.users.models import User
from enums.message_role import MessageRole


class TriggerSentinelSignalTests(TestCase):
    """Tests for the post_save signal that triggers user notes extraction."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    @patch(
        "apps.chat_messages.signals.trigger_sentinel_on_user_message"
        ".extract_user_notes"
    )
    def test_triggers_on_new_user_message(self, mock_task):
        """Test that extract_user_notes is called when a user message is created."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Hello coach",
        )

        mock_task.delay_on_commit.assert_called_once_with(msg.pk)

    @patch(
        "apps.chat_messages.signals.trigger_sentinel_on_user_message"
        ".extract_user_notes"
    )
    def test_does_not_trigger_on_coach_message(self, mock_task):
        """Test that extract_user_notes is NOT called for coach messages."""
        ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="Welcome!",
        )

        mock_task.delay_on_commit.assert_not_called()

    @patch(
        "apps.chat_messages.signals.trigger_sentinel_on_user_message"
        ".extract_user_notes"
    )
    def test_does_not_trigger_on_update(self, mock_task):
        """Test that extract_user_notes is NOT called when a message is updated."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Original",
        )

        mock_task.reset_mock()

        msg.content = "Updated"
        msg.save()

        mock_task.delay_on_commit.assert_not_called()

    @patch(
        "apps.chat_messages.signals.trigger_sentinel_on_user_message"
        ".extract_user_notes"
    )
    def test_skips_test_scenario_messages(self, mock_task):
        """Test that extraction is skipped for test scenario messages."""
        from apps.test_scenario.models import TestScenario

        scenario = TestScenario.objects.create(name="Test Scenario", template={})

        ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Test scenario message",
            test_scenario=scenario,
        )

        mock_task.delay_on_commit.assert_not_called()

    @patch(
        "apps.chat_messages.signals.trigger_sentinel_on_user_message"
        ".extract_user_notes"
    )
    def test_triggers_for_each_new_user_message(self, mock_task):
        """Test that each new user message triggers its own extraction."""
        msg1 = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="First",
        )
        msg2 = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Second",
        )

        self.assertEqual(mock_task.delay_on_commit.call_count, 2)
        mock_task.delay_on_commit.assert_any_call(msg1.pk)
        mock_task.delay_on_commit.assert_any_call(msg2.pk)
