"""
Tests for get_user_chat_messages function.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch

from apps.users.models import User
from apps.users.functions import get_user_chat_messages
from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole


class GetUserChatMessagesFunctionTests(TestCase):
    """Test the get_user_chat_messages function directly."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_returns_messages_in_chronological_order(self):
        """Test that messages are returned in chronological order (oldest first)."""
        # Create messages (oldest first)
        msg1 = ChatMessage.objects.create(
            user=self.user,
            content="First message",
            role=MessageRole.USER,
        )
        msg2 = ChatMessage.objects.create(
            user=self.user,
            content="Second message",
            role=MessageRole.COACH,
        )
        msg3 = ChatMessage.objects.create(
            user=self.user,
            content="Third message",
            role=MessageRole.USER,
        )

        messages = get_user_chat_messages(self.user)

        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0].content, "First message")
        self.assertEqual(messages[1].content, "Second message")
        self.assertEqual(messages[2].content, "Third message")

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_adds_initial_message_if_empty(self, mock_get_initial):
        """Test that initial message is added if chat is empty."""
        mock_get_initial.return_value = "Welcome to coaching!"

        messages = get_user_chat_messages(self.user)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Welcome to coaching!")
        self.assertEqual(messages[0].role, MessageRole.COACH)

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_no_initial_message_if_none_configured(self, mock_get_initial):
        """Test behavior when no initial message is configured."""
        mock_get_initial.return_value = None

        messages = get_user_chat_messages(self.user)

        self.assertEqual(len(messages), 0)

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_does_not_add_initial_if_messages_exist(self, mock_get_initial):
        """Test that initial message is not added if user already has messages."""
        mock_get_initial.return_value = "Welcome!"
        
        ChatMessage.objects.create(
            user=self.user,
            content="Existing message",
            role=MessageRole.USER,
        )

        messages = get_user_chat_messages(self.user)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Existing message")
        # get_initial_message should not be called if messages exist
        mock_get_initial.assert_not_called()

    def test_does_not_return_other_users_messages(self):
        """Test that function only returns messages for the specified user."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        ChatMessage.objects.create(
            user=self.user,
            content="My message",
            role=MessageRole.USER,
        )
        ChatMessage.objects.create(
            user=other_user,
            content="Other user message",
            role=MessageRole.USER,
        )

        messages = get_user_chat_messages(self.user)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "My message")


class GetUserChatMessagesAPITests(APITestCase):
    """Test the chat-messages API endpoint."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_returns_messages(self):
        """Test API endpoint returns messages."""
        ChatMessage.objects.create(
            user=self.user,
            content="Test message",
            role=MessageRole.USER,
        )

        response = self.client.get("/api/v1/user/me/chat-messages")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Test message")

    def test_api_requires_authentication(self):
        """Test that endpoint requires authentication."""
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/v1/user/me/chat-messages")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

