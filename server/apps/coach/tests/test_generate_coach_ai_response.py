"""
Tests for apps/coach/utils/generate_coach_ai_response.py
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from enums.ai import AIModel
from apps.coach.utils.generate_coach_ai_response import generate_coach_ai_response


class TestGenerateCoachAiResponse(SimpleTestCase):
    """Unit tests for generate_coach_ai_response."""

    def _make_mock_service(self, return_value=None):
        service = MagicMock()
        service.generate.return_value = return_value or MagicMock()
        return service

    @patch("apps.coach.utils.generate_coach_ai_response.AIServiceFactory")
    def test_creates_service_for_given_model(self, mock_factory):
        """AIServiceFactory.create is called with the model passed in."""
        mock_factory.create.return_value = self._make_mock_service()
        generate_coach_ai_response("prompt", [], MagicMock, AIModel.GPT_4O)
        mock_factory.create.assert_called_once_with(AIModel.GPT_4O)

    @patch("apps.coach.utils.generate_coach_ai_response.AIServiceFactory")
    def test_calls_generate_with_correct_args(self, mock_factory):
        """service.generate is called with prompt, history, format, and model."""
        mock_service = self._make_mock_service()
        mock_factory.create.return_value = mock_service
        mock_format = MagicMock()
        history = [MagicMock()]

        generate_coach_ai_response("my prompt", history, mock_format, AIModel.GPT_4O)

        mock_service.generate.assert_called_once_with(
            "my prompt", history, mock_format, AIModel.GPT_4O
        )

    @patch("apps.coach.utils.generate_coach_ai_response.AIServiceFactory")
    def test_returns_result_from_generate(self, mock_factory):
        """Returns whatever service.generate returns."""
        expected = MagicMock()
        mock_factory.create.return_value = self._make_mock_service(return_value=expected)
        result = generate_coach_ai_response("p", [], MagicMock, AIModel.GPT_4O)
        self.assertIs(result, expected)
