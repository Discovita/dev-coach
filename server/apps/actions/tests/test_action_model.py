"""
Tests for apps.actions.models.Action.

Verifies model creation, field defaults, constraints, indexes, and
string representation.
"""

from django.test import TestCase

from apps.actions.models import Action
from conftest import create_test_user, create_test_chat_message
from enums.action_type import ActionType
from enums.message_role import MessageRole


class ActionModelTests(TestCase):
    """Tests for the Action model."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_message = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Coach says hello"
        )

    def test_create_action(self):
        """Should create an Action with required fields."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={"name": "Visionary", "category": "passions_and_talents"},
            coach_message=self.coach_message,
        )
        self.assertIsNotNone(action.id)
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.action_type, ActionType.CREATE_IDENTITY.value)

    def test_id_is_uuid(self):
        """Action ID should be a UUID."""
        import uuid

        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        self.assertIsInstance(action.id, uuid.UUID)

    def test_timestamp_auto_set(self):
        """timestamp should be set automatically on creation."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        self.assertIsNotNone(action.timestamp)

    def test_updated_at_auto_set(self):
        """updated_at should be set automatically."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        self.assertIsNotNone(action.updated_at)

    def test_result_summary_is_optional(self):
        """result_summary should default to None."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.TRANSITION_PHASE.value,
            parameters={"to_phase": "get_to_know_you"},
            coach_message=self.coach_message,
        )
        self.assertIsNone(action.result_summary)

    def test_result_summary_can_be_set(self):
        """result_summary should accept text."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            result_summary="Created identity 'Visionary'",
            coach_message=self.coach_message,
        )
        self.assertEqual(action.result_summary, "Created identity 'Visionary'")

    def test_test_scenario_is_optional(self):
        """test_scenario should default to None."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        self.assertIsNone(action.test_scenario)

    def test_str_representation(self):
        """__str__ should include action type, email, and timestamp."""
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        result = str(action)
        self.assertIn(ActionType.CREATE_IDENTITY.value, result)
        self.assertIn(self.user.email, result)

    def test_ordering_by_timestamp(self):
        """Actions should be ordered by timestamp ascending."""
        a1 = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={"order": 1},
            coach_message=self.coach_message,
        )
        a2 = Action.objects.create(
            user=self.user,
            action_type=ActionType.TRANSITION_PHASE.value,
            parameters={"order": 2},
            coach_message=self.coach_message,
        )

        actions = list(Action.objects.filter(user=self.user))
        self.assertEqual(actions[0].id, a1.id)
        self.assertEqual(actions[1].id, a2.id)

    def test_cascade_deletes_with_user(self):
        """Actions should be deleted when the user is deleted."""
        Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        self.user.delete()
        self.assertEqual(Action.objects.count(), 0)

    def test_cascade_deletes_with_coach_message(self):
        """Actions should be deleted when the coach message is deleted."""
        Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_message,
        )
        self.coach_message.delete()
        self.assertEqual(Action.objects.count(), 0)

    def test_parameters_stores_json(self):
        """parameters field should store and retrieve JSON data."""
        params = {
            "name": "Visionary",
            "note": "Loves to create",
            "category": "passions_and_talents",
            "nested": {"key": "value"},
        }
        action = Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters=params,
            coach_message=self.coach_message,
        )
        action.refresh_from_db()
        self.assertEqual(action.parameters, params)
