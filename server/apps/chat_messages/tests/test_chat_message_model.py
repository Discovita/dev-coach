"""
Tests for the ChatMessage model.
"""

import uuid

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.users.models import User
from enums.message_role import MessageRole


class ChatMessageModelTests(TestCase):
    """Tests for ChatMessage model fields and behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_create_user_message(self):
        """Test creating a basic user message."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Hello coach",
        )

        self.assertIsInstance(msg.id, uuid.UUID)
        self.assertEqual(msg.user, self.user)
        self.assertEqual(msg.role, MessageRole.USER)
        self.assertEqual(msg.content, "Hello coach")
        self.assertIsNotNone(msg.timestamp)
        self.assertIsNone(msg.component_config)
        self.assertIsNone(msg.test_scenario)

    def test_create_coach_message(self):
        """Test creating a coach message."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="Welcome!",
        )

        self.assertEqual(msg.role, MessageRole.COACH)

    def test_str_representation(self):
        """Test __str__ formats as 'role:\\ncontent' for prompt formatting."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="How are you?",
        )

        self.assertEqual(str(msg), "User:\nHow are you?")

    def test_str_representation_coach(self):
        """Test __str__ for coach role."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="I'm doing well!",
        )

        self.assertEqual(str(msg), "Coach:\nI'm doing well!")

    def test_uuid_primary_key_auto_generated(self):
        """Test that UUID primary key is auto-generated."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Test",
        )

        self.assertIsInstance(msg.id, uuid.UUID)

    def test_component_config_stores_json(self):
        """Test that component_config accepts and stores JSON data."""
        config = {"type": "identity_card", "data": {"name": "Warrior"}}
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="Here's your identity",
            component_config=config,
        )

        msg.refresh_from_db()
        self.assertEqual(msg.component_config, config)

    def test_component_config_defaults_to_none(self):
        """Test that component_config defaults to None."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Test",
        )

        self.assertIsNone(msg.component_config)

    def test_cascade_delete_with_user(self):
        """Test that messages are deleted when user is deleted."""
        ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Message 1",
        )
        ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="Message 2",
        )

        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 2)

        self.user.delete()

        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_related_name_chat_messages(self):
        """Test that user.chat_messages reverse relation works."""
        ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Hello",
        )

        self.assertEqual(self.user.chat_messages.count(), 1)
        self.assertEqual(self.user.chat_messages.first().content, "Hello")

    def test_timestamp_auto_set(self):
        """Test that timestamp is automatically set on creation."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="Test",
        )

        self.assertIsNotNone(msg.timestamp)

    def test_messages_ordered_by_creation(self):
        """Test that messages can be ordered chronologically."""
        msg1 = ChatMessage.objects.create(
            user=self.user, role=MessageRole.USER, content="First"
        )
        msg2 = ChatMessage.objects.create(
            user=self.user, role=MessageRole.COACH, content="Second"
        )

        messages = ChatMessage.objects.filter(user=self.user).order_by("timestamp")
        self.assertEqual(list(messages), [msg1, msg2])
