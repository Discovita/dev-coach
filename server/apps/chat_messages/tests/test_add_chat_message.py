"""
Tests for the add_chat_message utility function.
"""

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import add_chat_message
from apps.users.models import User
from enums.message_role import MessageRole


class AddChatMessageTests(TestCase):
    """Tests for add_chat_message utility."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_creates_user_message(self):
        """Test creating a user message via the utility."""
        msg = add_chat_message(self.user, "Hello", MessageRole.USER)

        self.assertIsInstance(msg, ChatMessage)
        self.assertEqual(msg.user, self.user)
        self.assertEqual(msg.content, "Hello")
        self.assertEqual(msg.role, MessageRole.USER)

    def test_creates_coach_message(self):
        """Test creating a coach message via the utility."""
        msg = add_chat_message(self.user, "Welcome!", MessageRole.COACH)

        self.assertEqual(msg.role, MessageRole.COACH)
        self.assertEqual(msg.content, "Welcome!")

    def test_persists_to_database(self):
        """Test that the message is saved to the database."""
        add_chat_message(self.user, "Persisted message", MessageRole.USER)

        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 1)
        self.assertEqual(
            ChatMessage.objects.get(user=self.user).content, "Persisted message"
        )

    def test_returns_created_instance(self):
        """Test that the returned instance has a valid pk."""
        msg = add_chat_message(self.user, "Test", MessageRole.USER)

        self.assertIsNotNone(msg.pk)
        self.assertTrue(ChatMessage.objects.filter(pk=msg.pk).exists())

    def test_multiple_messages_for_same_user(self):
        """Test creating multiple messages for the same user."""
        add_chat_message(self.user, "First", MessageRole.USER)
        add_chat_message(self.user, "Response", MessageRole.COACH)
        add_chat_message(self.user, "Second", MessageRole.USER)

        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 3)
