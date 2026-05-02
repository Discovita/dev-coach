"""
Tests for services/ai/utils/openai/build_messages.py
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from services.ai.utils.openai.build_messages import build_messages


class TestBuildMessages(SimpleTestCase):
    """Unit tests for build_messages."""

    def test_empty_call_returns_empty_list(self):
        """Calling with no arguments returns an empty list."""
        self.assertEqual(build_messages(), [])

    def test_system_message_only(self):
        """A system_message alone produces a single system entry."""
        result = build_messages(system_message="You are a coach.")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "system")
        self.assertEqual(result[0]["content"], "You are a coach.")

    def test_coach_role_mapped_to_assistant(self):
        """ChatMessage with role='coach' must be sent as role='assistant'."""
        msg = MagicMock()
        msg.role = "coach"
        msg.content = "Hello!"
        result = build_messages(messages=[msg])
        self.assertEqual(result[0]["role"], "assistant")
        self.assertEqual(result[0]["content"], "Hello!")

    def test_user_role_preserved(self):
        """ChatMessage with role='user' is passed through unchanged."""
        msg = MagicMock()
        msg.role = "user"
        msg.content = "Hi."
        result = build_messages(messages=[msg])
        self.assertEqual(result[0]["role"], "user")

    def test_system_message_comes_before_history(self):
        """system_message is always the first entry."""
        msg = MagicMock()
        msg.role = "user"
        msg.content = "Q"
        result = build_messages(system_message="Sys", messages=[msg])
        self.assertEqual(result[0]["role"], "system")
        self.assertEqual(result[1]["role"], "user")

    def test_multiple_history_messages_ordered_correctly(self):
        """History messages are appended in order after the system message."""
        roles_contents = [("user", "Q1"), ("coach", "A1"), ("user", "Q2")]
        msgs = []
        for role, content in roles_contents:
            m = MagicMock()
            m.role = role
            m.content = content
            msgs.append(m)
        result = build_messages(messages=msgs)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[1]["role"], "assistant")  # coach → assistant
        self.assertEqual(result[2]["role"], "user")

