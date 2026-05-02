"""
Tests for apps/coach/utils/apply_coach_response_actions.py
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.coach.utils.apply_coach_response_actions import apply_coach_response_actions


class TestApplyCoachResponseActions(SimpleTestCase):
    """Unit tests for apply_coach_response_actions."""

    @patch("apps.coach.utils.apply_coach_response_actions.apply_coach_actions")
    def test_delegates_to_apply_coach_actions(self, mock_apply):
        """Calls apply_coach_actions with coach_state, response, and message."""
        mock_state = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_apply.return_value = (mock_state, None)

        apply_coach_response_actions(mock_state, mock_response, mock_message)

        mock_apply.assert_called_once_with(mock_state, mock_response, mock_message)

    @patch("apps.coach.utils.apply_coach_response_actions.apply_coach_actions")
    def test_returns_tuple_from_apply_coach_actions(self, mock_apply):
        """Returns the (updated_state, component_config) tuple from apply_coach_actions."""
        expected_state = MagicMock()
        expected_config = MagicMock()
        mock_apply.return_value = (expected_state, expected_config)

        result = apply_coach_response_actions(MagicMock(), MagicMock(), MagicMock())

        self.assertEqual(result, (expected_state, expected_config))

    @patch("apps.coach.utils.apply_coach_response_actions.apply_coach_actions")
    def test_returns_none_component_when_no_component(self, mock_apply):
        """Returns (state, None) when the coach response has no component."""
        mock_state = MagicMock()
        mock_apply.return_value = (mock_state, None)

        updated_state, component = apply_coach_response_actions(
            mock_state, MagicMock(), MagicMock()
        )

        self.assertIs(updated_state, mock_state)
        self.assertIsNone(component)
