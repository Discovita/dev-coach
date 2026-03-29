"""
Tests for the ChatMessageSerializer.
"""

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.chat_messages.serializers import ChatMessageSerializer
from apps.users.models import User
from enums.message_role import MessageRole


class ChatMessageSerializerTests(TestCase):
    """Tests for ChatMessageSerializer output and read-only behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.message = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="Hello there!",
        )

    def test_serializes_expected_fields(self):
        """Test that all expected fields are present in serialized output."""
        data = ChatMessageSerializer(self.message).data

        self.assertIn("id", data)
        self.assertIn("role", data)
        self.assertIn("content", data)
        self.assertIn("timestamp", data)
        self.assertIn("component_config", data)

    def test_does_not_expose_user_field(self):
        """Test that user FK is not included in serialized output."""
        data = ChatMessageSerializer(self.message).data

        self.assertNotIn("user", data)

    def test_does_not_expose_test_scenario_field(self):
        """Test that test_scenario is not included in serialized output."""
        data = ChatMessageSerializer(self.message).data

        self.assertNotIn("test_scenario", data)

    def test_serialized_values(self):
        """Test that serialized values match the model instance."""
        data = ChatMessageSerializer(self.message).data

        self.assertEqual(data["id"], str(self.message.id))
        self.assertEqual(data["role"], "coach")
        self.assertEqual(data["content"], "Hello there!")
        self.assertIsNone(data["component_config"])

    def test_serializes_component_config(self):
        """Test that component_config JSON is serialized correctly."""
        config = {"type": "card", "props": {"title": "Test"}}
        self.message.component_config = config
        self.message.save()

        data = ChatMessageSerializer(self.message).data

        self.assertEqual(data["component_config"], config)

    def test_serializes_many(self):
        """Test serializing a queryset of messages."""
        ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.USER,
            content="User message",
        )

        messages = ChatMessage.objects.filter(user=self.user)
        data = ChatMessageSerializer(messages, many=True).data

        self.assertEqual(len(data), 2)

    def test_field_count(self):
        """Test that exactly 5 fields are serialized."""
        data = ChatMessageSerializer(self.message).data

        self.assertEqual(len(data), 5)
