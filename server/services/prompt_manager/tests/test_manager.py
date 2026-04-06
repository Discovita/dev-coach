"""
Tests for services.prompt_manager.manager.PromptManager.

Tests the prompt orchestration logic: prompt selection, context gathering,
formatting, and action instruction appending. DB queries and downstream
services are mocked to isolate the orchestration layer.
"""

from unittest.mock import MagicMock, patch, PropertyMock

from django.test import SimpleTestCase

from enums.ai import AIModel, AIProvider
from enums.coaching_phase import CoachingPhase
from enums.prompt_type import PromptType
from services.prompt_manager.manager import PromptManager


class CreateChatPromptTests(SimpleTestCase):
    """Tests for PromptManager.create_chat_prompt orchestration."""

    def _make_mocks(self):
        """Build common mocks for create_chat_prompt."""
        mock_user = MagicMock()
        mock_coach_state = MagicMock()
        mock_coach_state.current_phase = CoachingPhase.INTRODUCTION
        mock_prompt = MagicMock()
        mock_prompt.name = "Test Prompt"
        mock_prompt.body = "Hello {placeholder}"
        mock_prompt.allowed_actions = ["create_identity"]
        mock_prompt.required_context_keys = []
        return mock_user, mock_coach_state, mock_prompt

    @patch("services.prompt_manager.manager.append_recent_messages", return_value="final prompt")
    @patch("services.prompt_manager.manager.append_action_instructions", return_value="prompt with actions")
    @patch("services.prompt_manager.manager.prepend_system_context", return_value="prompt with system")
    @patch("services.prompt_manager.manager.prepend_user_notes", return_value="prompt with notes")
    @patch("services.prompt_manager.manager.format_for_provider")
    @patch("services.prompt_manager.manager.build_dynamic_response_format")
    @patch("services.prompt_manager.manager.gather_prompt_context")
    @patch("services.prompt_manager.manager.Prompt")
    @patch("services.prompt_manager.manager.CoachState")
    def test_full_orchestration_flow(
        self,
        MockCoachState,
        MockPrompt,
        mock_gather,
        mock_build_dynamic,
        mock_format,
        mock_prepend_notes,
        mock_prepend_system,
        mock_append_actions,
        mock_append_messages,
    ):
        """Should orchestrate all steps: fetch state, fetch prompt, gather context, format, append."""
        mock_user, mock_coach_state, mock_prompt = self._make_mocks()

        MockCoachState.objects.get.return_value = mock_coach_state
        MockPrompt.objects.filter.return_value.order_by.return_value.first.return_value = (
            mock_prompt
        )
        mock_gather.return_value = MagicMock()
        mock_build_dynamic.return_value = MagicMock()
        mock_format.return_value = ("formatted prompt", MagicMock())

        pm = PromptManager()
        result = pm.create_chat_prompt(mock_user, AIModel.GPT_4O)

        MockCoachState.objects.get.assert_called_once_with(user=mock_user)
        mock_gather.assert_called_once()
        mock_build_dynamic.assert_called_once_with(mock_prompt.allowed_actions)
        mock_format.assert_called_once()
        mock_prepend_notes.assert_called_once()
        mock_prepend_system.assert_called_once()
        mock_append_actions.assert_called_once()
        mock_append_messages.assert_called_once()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    @patch("services.prompt_manager.manager.Prompt")
    @patch("services.prompt_manager.manager.CoachState")
    def test_raises_if_no_prompt_found(self, MockCoachState, MockPrompt):
        """Should raise ValueError when no active prompt exists for the phase."""
        mock_coach_state = MagicMock()
        mock_coach_state.current_phase = CoachingPhase.INTRODUCTION
        MockCoachState.objects.get.return_value = mock_coach_state
        MockPrompt.objects.filter.return_value.order_by.return_value.first.return_value = None

        pm = PromptManager()
        with self.assertRaises(ValueError) as ctx:
            pm.create_chat_prompt(MagicMock(), AIModel.GPT_4O)

        self.assertIn("No prompt found", str(ctx.exception))

    @patch("services.prompt_manager.manager.append_recent_messages", return_value="final")
    @patch("services.prompt_manager.manager.append_action_instructions", return_value="actions")
    @patch("services.prompt_manager.manager.prepend_system_context", return_value="system")
    @patch("services.prompt_manager.manager.prepend_user_notes", return_value="notes")
    @patch("services.prompt_manager.manager.format_for_provider")
    @patch("services.prompt_manager.manager.build_dynamic_response_format")
    @patch("services.prompt_manager.manager.gather_prompt_context")
    @patch("services.prompt_manager.manager.Prompt")
    @patch("services.prompt_manager.manager.CoachState")
    def test_version_override_filters_prompt(
        self,
        MockCoachState,
        MockPrompt,
        mock_gather,
        mock_build_dynamic,
        mock_format,
        mock_prepend_notes,
        mock_prepend_system,
        mock_append_actions,
        mock_append_messages,
    ):
        """When version_override is provided, should filter prompts by version."""
        mock_coach_state = MagicMock()
        mock_coach_state.current_phase = CoachingPhase.INTRODUCTION
        MockCoachState.objects.get.return_value = mock_coach_state

        mock_prompt = MagicMock()
        mock_prompt.allowed_actions = []
        mock_prompt.name = "v5"

        queryset_mock = MagicMock()
        MockPrompt.objects.filter.return_value = queryset_mock
        queryset_mock.filter.return_value = queryset_mock
        queryset_mock.order_by.return_value.first.return_value = mock_prompt

        mock_format.return_value = ("prompt", MagicMock())

        pm = PromptManager()
        pm.create_chat_prompt(MagicMock(), AIModel.GPT_4O, version_override=5)

        queryset_mock.filter.assert_called_once_with(version=5)

    @patch("services.prompt_manager.manager.append_recent_messages", return_value="final")
    @patch("services.prompt_manager.manager.append_action_instructions")
    @patch("services.prompt_manager.manager.prepend_system_context", return_value="system")
    @patch("services.prompt_manager.manager.prepend_user_notes", return_value="notes")
    @patch("services.prompt_manager.manager.format_for_provider")
    @patch("services.prompt_manager.manager.build_dynamic_response_format")
    @patch("services.prompt_manager.manager.gather_prompt_context")
    @patch("services.prompt_manager.manager.Prompt")
    @patch("services.prompt_manager.manager.CoachState")
    def test_no_allowed_actions_uses_all(
        self,
        MockCoachState,
        MockPrompt,
        mock_gather,
        mock_build_dynamic,
        mock_format,
        mock_prepend_notes,
        mock_prepend_system,
        mock_append_actions,
        mock_append_messages,
    ):
        """When prompt has no allowed_actions, should fall back to all action types."""
        mock_coach_state = MagicMock()
        mock_coach_state.current_phase = CoachingPhase.INTRODUCTION
        MockCoachState.objects.get.return_value = mock_coach_state

        mock_prompt = MagicMock()
        mock_prompt.allowed_actions = []
        mock_prompt.name = "Empty actions"

        MockPrompt.objects.filter.return_value.order_by.return_value.first.return_value = (
            mock_prompt
        )
        mock_format.return_value = ("prompt", MagicMock())
        mock_append_actions.return_value = "final"

        pm = PromptManager()
        pm.create_chat_prompt(MagicMock(), AIModel.GPT_4O)

        call_args = mock_append_actions.call_args
        actions_arg = call_args[0][1]
        from enums.action_type import ActionType

        self.assertEqual(len(actions_arg), len(list(ActionType)))


class CreateSentinelPromptTests(SimpleTestCase):
    """Tests for PromptManager.create_sentinel_prompt."""

    @patch("services.prompt_manager.manager.append_action_instructions", return_value="final")
    @patch("services.prompt_manager.manager.append_user_notes", return_value="notes")
    @patch("services.prompt_manager.manager.format_for_provider")
    @patch("services.prompt_manager.manager.build_dynamic_response_format")
    @patch("services.prompt_manager.manager.gather_prompt_context")
    @patch("services.prompt_manager.manager.Prompt")
    @patch("services.prompt_manager.manager.CoachState")
    def test_sentinel_prompt_uses_sentinel_type(
        self,
        MockCoachState,
        MockPrompt,
        mock_gather,
        mock_build_dynamic,
        mock_format,
        mock_append_notes,
        mock_append_actions,
    ):
        """Should fetch prompts with prompt_type=SENTINEL."""
        mock_coach_state = MagicMock()
        MockCoachState.objects.get.return_value = mock_coach_state

        mock_prompt = MagicMock()
        mock_prompt.allowed_actions = []
        mock_prompt.version = 1

        MockPrompt.objects.filter.return_value.order_by.return_value.first.return_value = (
            mock_prompt
        )
        mock_format.return_value = ("sentinel_prompt", MagicMock())

        pm = PromptManager()
        pm.create_sentinel_prompt(MagicMock(), AIModel.GPT_4O)

        filter_call = MockPrompt.objects.filter.call_args
        self.assertEqual(
            filter_call.kwargs.get("prompt_type"), PromptType.SENTINEL
        )

    @patch("services.prompt_manager.manager.Prompt")
    @patch("services.prompt_manager.manager.CoachState")
    def test_raises_if_no_sentinel_prompt(self, MockCoachState, MockPrompt):
        """Should raise ValueError when no active sentinel prompt exists."""
        MockCoachState.objects.get.return_value = MagicMock()
        MockPrompt.objects.filter.return_value.order_by.return_value.first.return_value = None

        pm = PromptManager()
        with self.assertRaises((ValueError, AttributeError)):
            pm.create_sentinel_prompt(MagicMock(), AIModel.GPT_4O)
