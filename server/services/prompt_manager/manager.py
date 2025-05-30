"""
Prompt manager for the coach chatbot service.
Handles prompt construction, context gathering, and formatting for LLM calls.
Follows a modular, extensible pattern for easy future expansion.
"""

from enums.ai import AIModel
from apps.coach_states.models import CoachState
from apps.prompts.models import Prompt
from apps.users.models import User
from enums.action_type import ActionType
from services.prompt_manager import gather_prompt_context, format_for_provider
from services.action_handler.utils.dynamic_schema import build_dynamic_response_format
from services.prompt_manager.utils import (
    append_action_instructions,
    prepend_system_context,
    append_recent_messages,
)
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


# NOTE: There might be other things we want to add in every time as well: user info (name, gender, age, etc.)
class PromptManager:
    """
    Manages prompt templates and generates formatted prompts with context for the coach chatbot.
    Centralizes prompt generation for different LLM providers and endpoints.
    Uses AIProvider enum for provider selection.
    """

    # TODO: Need to add identity_instructions to the prompt
    def create_chat_prompt(
        self, user: User, model: AIModel, version_override: int = None
    ) -> str:
        """
        Create a prompt for the chat endpoint using the user's context.
        Orchestrates context collection, prompt formatting, and action instructions.
        Args:
            user: The Django User instance for whom to build the prompt.
            version_override: Optional version number to override the default prompt version.
        Returns:
            str: prompt for the chat endpoint.
        """
        # 1. Retrieve the user's CoachState
        coach_state = CoachState.objects.get(user=user)
        log.debug(f"coach_state: {coach_state}")
        state_value = coach_state.current_phase

        # 2. Select the newest active prompt for this state (or override)
        prompt_queryset = Prompt.objects.filter(
            coaching_phase=state_value,
            is_active=True,
        )
        if version_override is not None:
            prompt_queryset = prompt_queryset.filter(version=version_override)
        prompt = prompt_queryset.order_by("-version").first()
        if not prompt:
            raise ValueError(f"No prompt found for state {state_value}")
        # 3. Gather context for the prompt
        prompt_context = gather_prompt_context(prompt, coach_state)
        log.debug(f"prompt_context: {prompt_context}")
        provider = AIModel.get_provider(model)
        log.debug(f"provider: {provider}")
        response_format_model = build_dynamic_response_format(prompt.allowed_actions)
        log.debug(f"response_format_model: {response_format_model}")
        coach_prompt, response_format = format_for_provider(
            prompt,
            prompt_context,
            provider,
            response_format=response_format_model,
        )
        log.debug(f"coach_prompt: {coach_prompt}")
        log.debug(f"response_format: {response_format}")

        coach_prompt = prepend_system_context(coach_prompt)
        # Append action instructions to the system message
        if prompt.allowed_actions:
            coach_prompt = append_action_instructions(
                coach_prompt, prompt.allowed_actions
            )
        else:
            log.warning(
                f"Prompt {prompt.id} has no allowed actions. Using all action instructions."
            )
            coach_prompt = append_action_instructions(
                coach_prompt, ActionType.get_all_actions()
            )
        log.debug(f"coach_prompt with actions: {coach_prompt}")

        # add the recent messages
        coach_prompt = append_recent_messages(coach_prompt, coach_state)

        return coach_prompt, response_format
