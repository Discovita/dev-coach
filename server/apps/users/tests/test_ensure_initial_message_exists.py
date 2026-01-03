"""
Tests for ensure_initial_message_exists utility.
"""

from django.test import TestCase
from unittest.mock import patch

from apps.users.models import User
from apps.users.utils import ensure_initial_message_exists
from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole


class EnsureInitialMessageExistsTests(TestCase):
    """Test the ensure_initial_message_exists utility function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_adds_message_when_chat_empty(self, mock_get_initial):
        """Test that message is added when chat is empty."""
        mock_get_initial.return_value = "Welcome!"
        
        result = ensure_initial_message_exists(self.user)
        
        self.assertTrue(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().content, "Welcome!")
        self.assertEqual(messages.first().role, MessageRole.COACH)

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_does_not_add_when_messages_exist(self, mock_get_initial):
        """Test that message is not added when chat already has messages."""
        mock_get_initial.return_value = "Welcome!"
        ChatMessage.objects.create(
            user=self.user,
            content="Existing message",
            role=MessageRole.USER,
        )
        
        result = ensure_initial_message_exists(self.user)
        
        self.assertFalse(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().content, "Existing message")

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_returns_false_when_no_initial_configured(self, mock_get_initial):
        """Test that function returns False when no initial message is configured."""
        mock_get_initial.return_value = None
        
        result = ensure_initial_message_exists(self.user)
        
        self.assertFalse(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 0)

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_does_not_affect_other_users(self, mock_get_initial):
        """Test that function only affects the specified user."""
        mock_get_initial.return_value = "Welcome!"
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        ensure_initial_message_exists(self.user)
        
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 1)
        self.assertEqual(ChatMessage.objects.filter(user=other_user).count(), 0)

