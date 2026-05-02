"""
Tests for apps.actions.serializers.ActionSerializer.

Verifies serialization output shape, nested coach_message serialization,
and computed fields.
"""

from django.test import TestCase

from apps.actions.models import Action
from apps.actions.serializers import ActionSerializer
from conftest import create_test_user, create_test_chat_message
from enums.action_type import ActionType
from enums.message_role import MessageRole


class ActionSerializerTests(TestCase):
    """Tests for ActionSerializer output."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_message = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Coach message"
        )
        self.action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={"name": "Visionary"},
            result_summary="Created identity",
            coach_message=self.coach_message,
        )

    def test_serialized_fields_present(self):
        """Serialized data should contain all expected fields."""
        data = ActionSerializer(self.action).data
        expected_fields = [
            "id",
            "user",
            "action_type",
            "action_type_display",
            "parameters",
            "result_summary",
            "timestamp",
            "updated_at",
            "timestamp_formatted",
            "coach_message",
            "test_scenario",
        ]
        for field in expected_fields:
            self.assertIn(field, data, f"Missing field: {field}")

    def test_action_type_display(self):
        """action_type_display should be the human-readable label."""
        data = ActionSerializer(self.action).data
        self.assertEqual(data["action_type_display"], "Create Identity")

    def test_timestamp_formatted(self):
        """timestamp_formatted should follow YYYY-MM-DD HH:MM:SS format."""
        data = ActionSerializer(self.action).data
        import re

        self.assertRegex(
            data["timestamp_formatted"],
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        )

    def test_nested_coach_message(self):
        """coach_message should be a nested serialized object."""
        data = ActionSerializer(self.action).data
        self.assertIsInstance(data["coach_message"], dict)
        self.assertIn("content", data["coach_message"])
        self.assertEqual(data["coach_message"]["content"], "Coach message")

    def test_all_fields_are_read_only(self):
        """All fields should be read-only per Meta.read_only_fields."""
        serializer = ActionSerializer()
        for field_name, field in serializer.fields.items():
            self.assertTrue(
                field.read_only,
                f"Field '{field_name}' should be read_only",
            )

    def test_parameters_json_preserved(self):
        """parameters should be serialized as JSON."""
        data = ActionSerializer(self.action).data
        self.assertEqual(data["parameters"], {"name": "Visionary"})
