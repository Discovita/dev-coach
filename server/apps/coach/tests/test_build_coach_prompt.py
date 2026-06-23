"""
Tests for apps/coach/utils/build_coach_prompt.py
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from enums.ai import AIModel
from apps.coach.utils.build_coach_prompt import build_coach_prompt


class TestBuildCoachPrompt(SimpleTestCase):
    """Unit tests for build_coach_prompt."""

    @patch("apps.coach.utils.build_coach_prompt.PromptManager")
    def test_creates_prompt_manager_and_delegates(self, MockPromptManager):
        """Delegates to PromptManager().create_chat_prompt with user and model."""
        mock_user = MagicMock()
        mock_model = AIModel.GPT_4O
        mock_result = ("Rendered prompt", "Final prompt")

        mock_instance = MagicMock()
        mock_instance.create_chat_prompt.return_value = mock_result
        MockPromptManager.return_value = mock_instance

        result = build_coach_prompt(mock_user, mock_model)

        MockPromptManager.assert_called_once()
        mock_instance.create_chat_prompt.assert_called_once_with(
            user=mock_user, model=mock_model, version_override=None
        )
        self.assertEqual(result, mock_result)

    @patch("apps.coach.utils.build_coach_prompt.CoachState")
    @patch("apps.coach.utils.build_coach_prompt.PromptManager")
    def test_pins_prompt_version_for_current_phase(
        self, MockPromptManager, MockCoachState
    ):
        """A prompt_versions entry for the current phase pins that version."""
        mock_instance = MagicMock()
        mock_instance.create_chat_prompt.return_value = ("p", "f")
        MockPromptManager.return_value = mock_instance
        MockCoachState.objects.get.return_value.current_phase = "get_to_know_you"

        build_coach_prompt(
            MagicMock(), AIModel.GPT_4O, prompt_versions={"get_to_know_you": 10}
        )

        self.assertEqual(
            mock_instance.create_chat_prompt.call_args.kwargs["version_override"], 10
        )

    @patch("apps.coach.utils.build_coach_prompt.CoachState")
    @patch("apps.coach.utils.build_coach_prompt.PromptManager")
    def test_version_pin_ignored_for_other_phase(
        self, MockPromptManager, MockCoachState
    ):
        """A pin for a different phase does not leak into the current phase."""
        mock_instance = MagicMock()
        mock_instance.create_chat_prompt.return_value = ("p", "f")
        MockPromptManager.return_value = mock_instance
        MockCoachState.objects.get.return_value.current_phase = "identity_warm_up"

        build_coach_prompt(
            MagicMock(), AIModel.GPT_4O, prompt_versions={"get_to_know_you": 10}
        )

        self.assertIsNone(
            mock_instance.create_chat_prompt.call_args.kwargs["version_override"]
        )

    @patch("apps.coach.utils.build_coach_prompt.PromptManager")
    def test_returns_tuple_from_prompt_manager(self, MockPromptManager):
        """Returns the exact tuple PromptManager produces."""
        expected = ("system prompt content", "final prompt shown to user")
        mock_instance = MagicMock()
        mock_instance.create_chat_prompt.return_value = expected
        MockPromptManager.return_value = mock_instance

        result = build_coach_prompt(MagicMock(), AIModel.GPT_4O)
        self.assertEqual(result, expected)
