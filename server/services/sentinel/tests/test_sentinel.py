"""
Tests for services.sentinel.sentinel.Sentinel.

Verifies the Sentinel service orchestration: prompt creation, AI call,
and action application. All external services are mocked.
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase


class SentinelInitTests(SimpleTestCase):
    """Tests for Sentinel initialization."""

    @patch("services.sentinel.sentinel.CoachState")
    @patch("services.sentinel.sentinel.PromptManager")
    def test_init_fetches_coach_state(self, MockPM, MockCoachState):
        """Sentinel should fetch the user's CoachState on init."""
        from services.sentinel.sentinel import Sentinel

        mock_user = MagicMock()
        mock_coach_state = MagicMock()
        MockCoachState.objects.get.return_value = mock_coach_state

        sentinel = Sentinel(mock_user)

        MockCoachState.objects.get.assert_called_once_with(user=mock_user)
        self.assertEqual(sentinel.coach_state, mock_coach_state)
        self.assertEqual(sentinel.user, mock_user)

    @patch("services.sentinel.sentinel.CoachState")
    @patch("services.sentinel.sentinel.PromptManager")
    def test_init_handles_missing_coach_state(self, MockPM, MockCoachState):
        """Should handle DoesNotExist gracefully."""
        from apps.coach_states.models import CoachState
        from services.sentinel.sentinel import Sentinel

        MockCoachState.DoesNotExist = CoachState.DoesNotExist
        MockCoachState.objects.get.side_effect = CoachState.DoesNotExist

        sentinel = Sentinel(MagicMock())
        self.assertFalse(hasattr(sentinel, "coach_state"))


class SentinelExtractNotesTests(SimpleTestCase):
    """Tests for Sentinel.extract_notes orchestration."""

    @patch("services.sentinel.sentinel.apply_coach_actions")
    @patch("services.sentinel.sentinel.AIServiceFactory")
    @patch("services.sentinel.sentinel.CoachState")
    @patch("services.sentinel.sentinel.PromptManager")
    def test_extract_notes_full_flow(
        self, MockPM, MockCoachState, MockAIFactory, mock_apply
    ):
        """Should build prompt, call AI, then apply actions."""
        from services.sentinel.sentinel import Sentinel

        mock_user = MagicMock()
        mock_coach_state = MagicMock()
        MockCoachState.objects.get.return_value = mock_coach_state

        mock_pm_instance = MagicMock()
        mock_pm_instance.create_sentinel_prompt.return_value = (
            "sentinel prompt",
            MagicMock(),
        )
        MockPM.return_value = mock_pm_instance

        mock_ai = MagicMock()
        mock_response = MagicMock()
        mock_ai.call_sentinel.return_value = mock_response
        MockAIFactory.create.return_value = mock_ai

        sentinel = Sentinel(mock_user)
        mock_chat_message = MagicMock()
        sentinel.extract_notes(mock_chat_message)

        mock_pm_instance.create_sentinel_prompt.assert_called_once()
        mock_ai.call_sentinel.assert_called_once()
        mock_apply.assert_called_once_with(
            mock_coach_state, mock_response, mock_chat_message
        )

    @patch("services.sentinel.sentinel.apply_coach_actions")
    @patch("services.sentinel.sentinel.AIServiceFactory")
    @patch("services.sentinel.sentinel.CoachState")
    @patch("services.sentinel.sentinel.PromptManager")
    def test_extract_notes_passes_response_format(
        self, MockPM, MockCoachState, MockAIFactory, mock_apply
    ):
        """Should pass the response_format from prompt manager to AI service."""
        from services.sentinel.sentinel import Sentinel

        MockCoachState.objects.get.return_value = MagicMock()
        mock_response_format = MagicMock()
        MockPM.return_value.create_sentinel_prompt.return_value = (
            "prompt",
            mock_response_format,
        )

        mock_ai = MagicMock()
        MockAIFactory.create.return_value = mock_ai

        sentinel = Sentinel(MagicMock())
        sentinel.extract_notes(MagicMock())

        call_args = mock_ai.call_sentinel.call_args
        self.assertEqual(call_args[0][1], mock_response_format)
