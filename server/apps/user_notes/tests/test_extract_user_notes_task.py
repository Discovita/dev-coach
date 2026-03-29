"""
Tests for the extract_user_notes Celery task.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.user_notes.tasks import extract_user_notes
from apps.users.models import User


class TestExtractUserNotesTask(TestCase):
    """Tests for the extract_user_notes Celery task."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="taskuser@test.com",
            password="TestPass123!",
            first_name="Task",
            last_name="User",
        )
        cls.message = ChatMessage.objects.create(
            user=cls.user,
            role="user",
            content="I really enjoy cooking Italian food.",
        )

    @patch("apps.user_notes.tasks.extract_user_notes.Sentinel")
    def test_task_instantiates_sentinel_with_user(self, MockSentinel):
        mock_instance = MagicMock()
        MockSentinel.return_value = mock_instance

        extract_user_notes(str(self.message.id))

        MockSentinel.assert_called_once_with(self.user)

    @patch("apps.user_notes.tasks.extract_user_notes.Sentinel")
    def test_task_calls_extract_notes_with_message(self, MockSentinel):
        mock_instance = MagicMock()
        MockSentinel.return_value = mock_instance

        extract_user_notes(str(self.message.id))

        mock_instance.extract_notes.assert_called_once()
        call_arg = mock_instance.extract_notes.call_args[0][0]
        self.assertEqual(call_arg.id, self.message.id)

    @patch("apps.user_notes.tasks.extract_user_notes.Sentinel")
    def test_task_raises_on_missing_message(self, MockSentinel):
        import uuid

        with self.assertRaises(ChatMessage.DoesNotExist):
            extract_user_notes(str(uuid.uuid4()))

        MockSentinel.assert_not_called()
