"""
Tests for services.action_handler.handler (apply_coach_actions, apply_component_actions).

Uses mocks to isolate the orchestration logic from individual action handlers.
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from enums.action_type import ActionType
from services.action_handler.handler import (
    ACTION_REGISTRY,
    apply_coach_actions,
    apply_component_actions,
)


class ActionRegistryTests(SimpleTestCase):
    """Tests for the ACTION_REGISTRY mapping."""

    def test_registry_maps_action_type_values_to_functions(self):
        """Every key should be a valid ActionType value string."""
        for key in ACTION_REGISTRY:
            self.assertIn(
                key,
                [a.value for a in ActionType],
                f"Registry key '{key}' is not a valid ActionType value",
            )

    def test_registry_values_are_callable(self):
        """Every registry value should be callable."""
        for key, handler in ACTION_REGISTRY.items():
            self.assertTrue(callable(handler), f"Handler for '{key}' is not callable")

    def test_all_non_component_action_types_have_handlers(self):
        """Core action types should be in the registry."""
        essential_actions = [
            ActionType.CREATE_IDENTITY,
            ActionType.TRANSITION_PHASE,
            ActionType.ACCEPT_IDENTITY,
            ActionType.UPDATE_IDENTITY,
            ActionType.ADD_USER_NOTE,
        ]
        for action in essential_actions:
            self.assertIn(action.value, ACTION_REGISTRY)


class ApplyCoachActionsTests(SimpleTestCase):
    """Tests for apply_coach_actions orchestration."""

    def _make_mock_response(self, actions_dict):
        """Build a mock CoachChatResponse with given action fields."""
        response = MagicMock()
        dump = {"message": "Test response", **actions_dict}
        response.model_dump.return_value = dump

        for key, value in actions_dict.items():
            action_obj = MagicMock()
            action_obj.params = MagicMock()
            action_obj.params.model_dump.return_value = {"test": "data"}
            setattr(response, key, action_obj)

        response.message = "Test response"
        return response

    def _make_mock_coach_state(self):
        coach_state = MagicMock()
        coach_state.user = MagicMock()
        coach_state.user.test_scenario = None
        return coach_state

    def test_skips_message_field(self):
        """The 'message' field should not be processed as an action."""
        response = self._make_mock_response({})
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        apply_coach_actions(coach_state, response, coach_message)
        coach_state.refresh_from_db.assert_called_once()

    @patch.dict(
        "services.action_handler.handler.ACTION_REGISTRY",
        {"create_identity": MagicMock(return_value=None)},
    )
    def test_calls_registered_handler(self):
        """Should call the handler function for a known action."""
        from services.action_handler.handler import ACTION_REGISTRY

        response = self._make_mock_response(
            {ActionType.CREATE_IDENTITY.value: True}
        )
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        apply_coach_actions(coach_state, response, coach_message)
        ACTION_REGISTRY["create_identity"].assert_called_once()

    def test_skips_none_actions(self):
        """Actions with None value should be skipped."""
        response = MagicMock()
        response.model_dump.return_value = {
            "message": "Hello",
            "create_identity": None,
        }
        response.create_identity = None
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        updated_state, component = apply_coach_actions(
            coach_state, response, coach_message
        )
        coach_state.refresh_from_db.assert_called_once()

    @patch.dict(
        "services.action_handler.handler.ACTION_REGISTRY",
        {"add_user_note": MagicMock(return_value=None)},
    )
    def test_sentinel_actions_skip_coach_message_param(self):
        """Sentinel actions (add/update/delete user note) should NOT receive coach_message."""
        from services.action_handler.handler import ACTION_REGISTRY

        response = self._make_mock_response(
            {ActionType.ADD_USER_NOTE.value: True}
        )
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        apply_coach_actions(coach_state, response, coach_message)

        call_args = ACTION_REGISTRY["add_user_note"].call_args
        self.assertEqual(len(call_args[0]), 2)

    def test_returns_tuple_of_coach_state_and_component(self):
        """Should return (coach_state, component_config) tuple."""
        response = self._make_mock_response({})
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        result = apply_coach_actions(coach_state, response, coach_message)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_component_config_defaults_to_none(self):
        """component_config should be None when no action returns one."""
        response = self._make_mock_response({})
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        _, component = apply_coach_actions(coach_state, response, coach_message)
        self.assertIsNone(component)

    def test_warns_on_unregistered_action(self):
        """Should log a warning for unknown action types without crashing."""
        response = MagicMock()
        response.model_dump.return_value = {
            "message": "Hello",
            "unknown_action": "data",
        }
        action_obj = MagicMock()
        action_obj.params = MagicMock()
        response.unknown_action = action_obj
        coach_state = self._make_mock_coach_state()
        coach_message = MagicMock()

        updated_state, component = apply_coach_actions(
            coach_state, response, coach_message
        )
        self.assertIsNone(component)


class ApplyComponentActionsTests(SimpleTestCase):
    """Tests for apply_component_actions orchestration."""

    def _make_component_action(self, action_type, params):
        ca = MagicMock()
        ca.action = action_type
        ca.params = params
        return ca

    @patch.dict(
        "services.action_handler.handler.ACTION_REGISTRY",
        {"accept_identity": MagicMock(return_value=None)},
    )
    def test_calls_handler_for_component_action(self):
        """Should dispatch component actions to the correct handler."""
        from services.action_handler.handler import ACTION_REGISTRY

        ca = self._make_component_action("accept_identity", {"id": "some-uuid"})
        coach_state = MagicMock()
        user_message = MagicMock()

        apply_component_actions(coach_state, [ca], user_message)
        ACTION_REGISTRY["accept_identity"].assert_called_once()

    def test_skips_action_with_missing_type(self):
        """Should skip component actions with no action field."""
        ca = self._make_component_action(None, {})
        coach_state = MagicMock()
        user_message = MagicMock()

        result = apply_component_actions(coach_state, [ca], user_message)
        coach_state.refresh_from_db.assert_called_once()

    def test_returns_updated_coach_state(self):
        """Should return the coach_state after refresh."""
        coach_state = MagicMock()
        user_message = MagicMock()

        result = apply_component_actions(coach_state, [], user_message)
        coach_state.refresh_from_db.assert_called_once()
