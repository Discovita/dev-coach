"""
Tests for create_scenario_chat_messages function.
"""

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.test_scenario.utils import create_scenario_chat_messages
from apps.test_scenario.models import TestScenario
from apps.users.models import User


def _make_scenario(name="Chat Scenario"):
    return TestScenario.objects.create(
        name=name,
        template={"user": {"first_name": "Test", "last_name": "User"}},
    )


class TestCreateScenarioChatMessages(TestCase):
    """create_scenario_chat_messages tests."""

    def setUp(self):
        self.scenario = _make_scenario()
        self.user = User.objects.create_user(
            email="create_cm@example.com", password="testpass",
            test_scenario=self.scenario,
        )

    # ==================== Creation ====================

    def test_creates_messages_from_template(self):
        """Should create one ChatMessage per entry in the template."""
        template = {
            "chat_messages": [
                {"role": "user", "content": "Hello"},
                {"role": "coach", "content": "Hi there"},
            ]
        }
        create_scenario_chat_messages(self.scenario, template, self.user)
        count = ChatMessage.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).count()
        self.assertEqual(count, 2)

    def test_returns_mapping_dict(self):
        """Should return a non-empty mapping dict."""
        template = {
            "chat_messages": [{"role": "user", "content": "Hello"}]
        }
        mapping = create_scenario_chat_messages(self.scenario, template, self.user)
        self.assertIsInstance(mapping, dict)
        self.assertEqual(len(mapping), 1)

    def test_mapping_key_format(self):
        """Mapping keys should follow 'role|content|timestamp' format."""
        template = {
            "chat_messages": [{"role": "user", "content": "Hello"}]
        }
        mapping = create_scenario_chat_messages(self.scenario, template, self.user)
        key = list(mapping.keys())[0]
        self.assertTrue(key.startswith("user|Hello|"))

    def test_mapping_values_are_chat_message_instances(self):
        """Mapping values should be ChatMessage instances."""
        template = {
            "chat_messages": [{"role": "user", "content": "Hello"}]
        }
        mapping = create_scenario_chat_messages(self.scenario, template, self.user)
        msg = list(mapping.values())[0]
        self.assertIsInstance(msg, ChatMessage)

    # ==================== Idempotency ====================

    def test_deletes_existing_messages_before_creating(self):
        """Should delete previous messages for the same scenario/user before re-creating."""
        template = {
            "chat_messages": [{"role": "user", "content": "First run"}]
        }
        create_scenario_chat_messages(self.scenario, template, self.user)
        create_scenario_chat_messages(self.scenario, template, self.user)
        count = ChatMessage.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).count()
        self.assertEqual(count, 1)
