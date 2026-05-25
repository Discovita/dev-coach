"""
Tests for apps/coach/utils/build_coach_response_data.py
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.coach.utils.build_coach_response_data import build_coach_response_data


class TestBuildCoachResponseData(SimpleTestCase):
    """Unit tests for build_coach_response_data."""

    def test_returns_message_and_prompt(self):
        """Result always contains 'message' and 'final_prompt'."""
        result = build_coach_response_data("Hello!", "System prompt here.", False)
        self.assertEqual(result["message"], "Hello!")
        self.assertEqual(result["final_prompt"], "System prompt here.")

    def test_no_component_config_omits_component_key(self):
        """When component_config is None, 'component' is not in the result."""
        result = build_coach_response_data("Hi", "Prompt", False, component_config=None)
        self.assertNotIn("component", result)

    def test_default_component_config_is_none(self):
        """component_config defaults to None when not supplied."""
        result = build_coach_response_data("Hi", "Prompt", False)
        self.assertNotIn("component", result)

    def test_component_config_included_when_provided(self):
        """When component_config is provided, 'component' is in the result."""
        mock_config = MagicMock()
        mock_config.model_dump.return_value = {"type": "accept_identity", "data": {}}
        result = build_coach_response_data(
            "Hi", "Prompt", False, component_config=mock_config
        )
        self.assertIn("component", result)
        self.assertEqual(result["component"], {"type": "accept_identity", "data": {}})

    def test_component_config_calls_model_dump(self):
        """build_coach_response_data serializes the component via model_dump()."""
        mock_config = MagicMock()
        mock_config.model_dump.return_value = {"key": "value"}
        build_coach_response_data("Hi", "Prompt", False, component_config=mock_config)
        mock_config.model_dump.assert_called_once()

    def test_coach_response_includes_on_break_field(self):
        """The returned dict always carries the `on_break` key."""
        result_false = build_coach_response_data("Hi", "Prompt", False)
        self.assertIn("on_break", result_false)
        self.assertFalse(result_false["on_break"])

        result_true = build_coach_response_data("Hi", "Prompt", True)
        self.assertIn("on_break", result_true)
        self.assertTrue(result_true["on_break"])
