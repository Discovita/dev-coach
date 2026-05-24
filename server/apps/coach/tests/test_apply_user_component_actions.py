"""
Tests for apps/coach/utils/apply_user_component_actions.py
"""

from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from apps.coach.utils.apply_user_component_actions import apply_user_component_actions
from models.components.ComponentConfig import ComponentAction


class TestApplyUserComponentActions(SimpleTestCase):
    """Unit tests for apply_user_component_actions."""

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_does_nothing_when_actions_is_none(self, mock_apply):
        """Returns early without calling apply_component_actions when None is passed."""
        apply_user_component_actions(MagicMock(), MagicMock(), None)
        mock_apply.assert_not_called()

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_does_nothing_when_actions_is_empty_list(self, mock_apply):
        """Returns early without calling apply_component_actions for an empty list."""
        apply_user_component_actions(MagicMock(), MagicMock(), [])
        mock_apply.assert_not_called()

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_converts_dicts_to_component_actions(self, mock_apply):
        """Dict items are converted to ComponentAction instances before delegating."""
        mock_apply.return_value = (MagicMock(), None)
        coach_state = MagicMock()
        chat_message = MagicMock()
        action_dict = {"action": "accept_identity", "params": {"identity_id": "abc"}}

        apply_user_component_actions(coach_state, chat_message, [action_dict])

        args, _ = mock_apply.call_args
        component_actions = args[1]
        self.assertEqual(len(component_actions), 1)
        self.assertIsInstance(component_actions[0], ComponentAction)

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_passes_through_existing_component_action_objects(self, mock_apply):
        """ComponentAction objects are passed through without re-wrapping."""
        mock_apply.return_value = (MagicMock(), None)
        coach_state = MagicMock()
        chat_message = MagicMock()
        existing_action = ComponentAction(action="accept_identity", params={})

        apply_user_component_actions(coach_state, chat_message, [existing_action])

        args, _ = mock_apply.call_args
        component_actions = args[1]
        self.assertIs(component_actions[0], existing_action)

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_calls_apply_component_actions_with_state_and_message(self, mock_apply):
        """Passes coach_state and user_chat_message correctly to apply_component_actions."""
        mock_apply.return_value = (MagicMock(), None)
        coach_state = MagicMock()
        chat_message = MagicMock()
        action_dict = {"action": "some_action", "params": {}}

        apply_user_component_actions(coach_state, chat_message, [action_dict])

        args, _ = mock_apply.call_args
        self.assertIs(args[0], coach_state)
        self.assertIs(args[2], chat_message)

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_returns_none_when_no_actions(self, mock_apply):
        """Returns None when actions list is empty or None — no dispatch needed."""
        self.assertIsNone(
            apply_user_component_actions(MagicMock(), MagicMock(), None)
        )
        self.assertIsNone(
            apply_user_component_actions(MagicMock(), MagicMock(), [])
        )
        mock_apply.assert_not_called()

    @patch("apps.coach.utils.apply_user_component_actions.apply_component_actions")
    def test_returns_component_config_from_apply_component_actions(self, mock_apply):
        """Propagates the ComponentConfig returned by apply_component_actions
        so the orchestrator can apply PR 10's skip-LLM rule."""
        sentinel_config = MagicMock(name="component_config")
        mock_apply.return_value = (MagicMock(), sentinel_config)
        coach_state = MagicMock()
        chat_message = MagicMock()
        action_dict = {"action": "start_break", "params": {"session_key": "x"}}

        result = apply_user_component_actions(
            coach_state, chat_message, [action_dict]
        )

        self.assertIs(result, sentinel_config)
