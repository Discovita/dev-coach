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
            user=mock_user, model=mock_model
        )
        self.assertEqual(result, mock_result)

    @patch("apps.coach.utils.build_coach_prompt.PromptManager")
    def test_returns_tuple_from_prompt_manager(self, MockPromptManager):
        """Returns the exact tuple PromptManager produces."""
        expected = ("system prompt content", "final prompt shown to user")
        mock_instance = MagicMock()
        mock_instance.create_chat_prompt.return_value = expected
        MockPromptManager.return_value = mock_instance

        result = build_coach_prompt(MagicMock(), AIModel.GPT_4O)
        self.assertEqual(result, expected)
