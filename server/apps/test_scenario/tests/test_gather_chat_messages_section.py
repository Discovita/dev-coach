"""
Tests for gather_chat_messages_section function.
"""

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.test_scenario.utils import gather_chat_messages_section
from apps.users.models import User


class TestGatherChatMessagesSection(TestCase):
    """gather_chat_messages_section tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="gather_cm@example.com", password="testpass"
        )

    # ==================== Empty case ====================

    def test_returns_empty_lists_when_no_messages(self):
        """Should return two empty collections when the user has no messages."""
        section, mapping = gather_chat_messages_section(self.user)
        self.assertEqual(section, [])
        self.assertEqual(mapping, {})

    # ==================== Basic output ====================

    def test_section_contains_role_and_content(self):
        """Each section entry should have role and content."""
        ChatMessage.objects.create(user=self.user, role="user", content="Hello")
        section, _ = gather_chat_messages_section(self.user)
        self.assertEqual(len(section), 1)
        self.assertEqual(section[0]["role"], "user")
        self.assertEqual(section[0]["content"], "Hello")

    def test_mapping_keyed_by_message_id(self):
        """Mapping should be keyed by the original message UUID string."""
        msg = ChatMessage.objects.create(user=self.user, role="coach", content="Hi")
        _, mapping = gather_chat_messages_section(self.user)
        self.assertIn(str(msg.id), mapping)

    def test_mapping_entry_contains_expected_fields(self):
        """Each mapping entry should have role, content, timestamp, component_config."""
        ChatMessage.objects.create(user=self.user, role="coach", content="Hi")
        _, mapping = gather_chat_messages_section(self.user)
        entry = list(mapping.values())[0]
        self.assertIn("role", entry)
        self.assertIn("content", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("component_config", entry)

    # ==================== Ordering ====================

    def test_section_ordered_by_timestamp(self):
        """Section entries should be returned in ascending timestamp order."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        # timestamp is auto_now_add, so we create then update to set exact values
        msg_second = ChatMessage.objects.create(
            user=self.user, role="coach", content="Second"
        )
        msg_first = ChatMessage.objects.create(
            user=self.user, role="user", content="First"
        )
        ChatMessage.objects.filter(pk=msg_second.pk).update(
            timestamp=now + timedelta(seconds=1)
        )
        ChatMessage.objects.filter(pk=msg_first.pk).update(timestamp=now)

        section, _ = gather_chat_messages_section(self.user)
        self.assertEqual(section[0]["content"], "First")
        self.assertEqual(section[1]["content"], "Second")

    # ==================== Optional fields ====================

    def test_timestamp_included_when_present(self):
        """Should include timestamp as ISO string when message has a timestamp."""
        from django.utils import timezone
        now = timezone.now()
        ChatMessage.objects.create(
            user=self.user, role="user", content="Msg", timestamp=now
        )
        section, _ = gather_chat_messages_section(self.user)
        self.assertIn("timestamp", section[0])

    def test_component_config_included_when_present(self):
        """Should include component_config when present on the message."""
        ChatMessage.objects.create(
            user=self.user, role="coach", content="Msg",
            component_config={"type": "card"}
        )
        section, _ = gather_chat_messages_section(self.user)
        self.assertIn("component_config", section[0])
        self.assertEqual(section[0]["component_config"], {"type": "card"})

    def test_does_not_include_other_users_messages(self):
        """Should only return messages for the specified user."""
        other = User.objects.create_user(
            email="other_gather_cm@example.com", password="testpass"
        )
        ChatMessage.objects.create(user=other, role="user", content="Other msg")
        section, _ = gather_chat_messages_section(self.user)
        self.assertEqual(section, [])
