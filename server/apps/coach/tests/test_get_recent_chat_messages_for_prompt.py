"""
Tests for apps/coach/utils/get_recent_chat_messages_for_prompt.py
"""

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.coach.utils.get_recent_chat_messages_for_prompt import (
    get_recent_chat_messages_for_prompt,
)
from apps.users.models import User
from enums.message_role import MessageRole


class TestGetRecentChatMessagesForPrompt(TestCase):
    """Tests for get_recent_chat_messages_for_prompt."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="coach@example.com", password="Pass1!"
        )

    def test_returns_empty_list_when_no_messages(self):
        """Returns an empty list when the user has no chat history."""
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result, [])

    def test_returns_list_of_chat_messages(self):
        """Returns ChatMessage instances."""
        ChatMessage.objects.create(
            user=self.user, content="Hello", role=MessageRole.USER
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ChatMessage)

    def test_messages_ordered_oldest_first(self):
        """Messages are returned in chronological order (oldest → newest)."""
        m1 = ChatMessage.objects.create(
            user=self.user, content="First", role=MessageRole.USER
        )
        m2 = ChatMessage.objects.create(
            user=self.user, content="Second", role=MessageRole.COACH
        )
        m3 = ChatMessage.objects.create(
            user=self.user, content="Third", role=MessageRole.USER
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result[0].id, m1.id)
        self.assertEqual(result[1].id, m2.id)
        self.assertEqual(result[2].id, m3.id)

    def test_returns_only_five_most_recent_by_default(self):
        """Only the 5 most recent messages are returned by default."""
        for i in range(7):
            ChatMessage.objects.create(
                user=self.user, content=f"Message {i}", role=MessageRole.USER
            )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(len(result), 5)

    def test_custom_count_respected(self):
        """The count parameter controls how many messages are returned."""
        for i in range(10):
            ChatMessage.objects.create(
                user=self.user, content=f"Msg {i}", role=MessageRole.USER
            )
        result = get_recent_chat_messages_for_prompt(self.user, count=3)
        self.assertEqual(len(result), 3)

    def test_does_not_return_other_users_messages(self):
        """Messages belonging to other users are not included."""
        other_user = User.objects.create_user(
            email="other@example.com", password="Pass1!"
        )
        ChatMessage.objects.create(
            user=other_user, content="Not mine", role=MessageRole.USER
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result, [])
