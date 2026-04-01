"""
Tests for apps/coach/serializers/coach_request_serializer.py
         apps/coach/serializers/admin_coach_request_serializer.py
"""

from django.test import SimpleTestCase

from apps.coach.serializers.admin_coach_request_serializer import (
    AdminCoachRequestSerializer,
)
from apps.coach.serializers.coach_request_serializer import CoachRequestSerializer
from enums.ai import AIModel


class TestCoachRequestSerializer(SimpleTestCase):
    """Validation tests for CoachRequestSerializer."""

    def test_valid_with_message_only(self):
        """A plain message string is sufficient."""
        s = CoachRequestSerializer(data={"message": "Hello coach"})
        self.assertTrue(s.is_valid(), s.errors)

    def test_valid_with_message_and_actions(self):
        """Message and a well-formed actions list both validate."""
        s = CoachRequestSerializer(
            data={
                "message": "Hello",
                "actions": [{"action": "accept_identity", "params": {"id": "1"}}],
            }
        )
        self.assertTrue(s.is_valid(), s.errors)

    def test_actions_only_without_message_is_invalid(self):
        """message is a required field; actions alone fails field-level validation."""
        s = CoachRequestSerializer(
            data={"actions": [{"action": "accept_identity", "params": {}}]}
        )
        self.assertFalse(s.is_valid())
        self.assertIn("message", s.errors)

    def test_empty_body_is_invalid(self):
        """Neither message nor actions → validation error."""
        s = CoachRequestSerializer(data={})
        self.assertFalse(s.is_valid())

    def test_empty_message_and_no_actions_is_invalid(self):
        """Empty string message without actions → validation error."""
        s = CoachRequestSerializer(data={"message": ""})
        self.assertFalse(s.is_valid())

    def test_action_missing_action_key_is_invalid(self):
        """Actions item without 'action' key → validation error."""
        s = CoachRequestSerializer(
            data={"message": "Hi", "actions": [{"params": {}}]}
        )
        self.assertFalse(s.is_valid())

    def test_action_missing_params_key_is_invalid(self):
        """Actions item without 'params' key → validation error."""
        s = CoachRequestSerializer(
            data={"message": "Hi", "actions": [{"action": "accept_identity"}]}
        )
        self.assertFalse(s.is_valid())

    def test_action_item_not_a_dict_is_invalid(self):
        """Actions items that are not dicts → validation error."""
        s = CoachRequestSerializer(
            data={"message": "Hi", "actions": ["not_a_dict"]}
        )
        self.assertFalse(s.is_valid())

    def test_get_model_returns_default_when_no_model_name(self):
        """get_model() returns GPT_4O when model_name is absent."""
        s = CoachRequestSerializer(data={"message": "Hello"})
        s.is_valid()
        self.assertEqual(s.get_model(), AIModel.get_or_default(None))

    def test_get_model_with_explicit_model_name(self):
        """get_model() returns the model matching the provided model_name."""
        model = AIModel.GPT_4O
        s = CoachRequestSerializer(data={"message": "Hi", "model_name": model.value})
        s.is_valid()
        self.assertEqual(s.get_model(), model)


class TestAdminCoachRequestSerializer(SimpleTestCase):
    """Validation tests for AdminCoachRequestSerializer."""

    _VALID_UUID = "12345678-1234-5678-1234-567812345678"

    def test_valid_with_all_fields(self):
        """user_id + message → valid."""
        s = AdminCoachRequestSerializer(
            data={"user_id": self._VALID_UUID, "message": "Hello"}
        )
        self.assertTrue(s.is_valid(), s.errors)

    def test_missing_user_id_is_invalid(self):
        """user_id is required for admin requests."""
        s = AdminCoachRequestSerializer(data={"message": "Hello"})
        self.assertFalse(s.is_valid())

    def test_invalid_uuid_format_is_rejected(self):
        """A non-UUID user_id string is rejected."""
        s = AdminCoachRequestSerializer(
            data={"user_id": "not-a-uuid", "message": "Hello"}
        )
        self.assertFalse(s.is_valid())

    def test_inherits_message_validation(self):
        """AdminCoachRequestSerializer also requires message or actions."""
        s = AdminCoachRequestSerializer(data={"user_id": self._VALID_UUID})
        self.assertFalse(s.is_valid())
