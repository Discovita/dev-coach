"""
Prompt manager for the coach chatbot service.
Handles prompt construction, context gathering, and formatting for LLM calls.
Follows a modular, extensible pattern for easy future expansion.
"""

from enums.ai import AIModel, AIProvider
from apps.coach_states.models import CoachState
from apps.prompts.models import Prompt
from apps.users.models import User
from enums.action_type import ActionType
from services.prompt_manager import gather_prompt_context, format_for_provider
from services.action_handler.utils.dynamic_schema import build_dynamic_response_format
from services.prompt_manager.utils.append_action_instructions import (
    append_action_instructions,
)

# Import utilities (to be implemented next)
# from .collect_chat_context import collect_chat_context
# from .format_chat_prompt_for_provider import format_chat_prompt_for_provider
# from .action_instructions import append_action_instructions


class PromptManager:
    """
    Manages prompt templates and generates formatted prompts with context for the coach chatbot.
    Centralizes prompt generation for different LLM providers and endpoints.
    Uses AIProvider enum for provider selection.
    """

    async def create_chat_prompt(
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
        coach_state = await CoachState.objects.aget(user=user)
        state_value = coach_state.current_state

        # 2. Select the newest active prompt for this state (or override)
        prompt_qs = Prompt.objects.filter(
            coach_state=state_value,
            is_active=True,
        )
        if version_override is not None:
            prompt_qs = prompt_qs.filter(version=version_override)
        prompt = prompt_qs.order_by("-version").first()
        if not prompt:
            raise ValueError(f"No prompt found for state {state_value}")

        # 3. Gather context for the prompt
        prompt_context = await gather_prompt_context(prompt, coach_state)
        provider = AIModel.get_provider(model)
        response_format_model = await build_dynamic_response_format(
            prompt.allowed_actions
        )
        coach_prompt, response_format = await format_for_provider(
            prompt, prompt_context, provider, response_format=response_format_model
        )

        # Append action instructions to the system message
        if prompt.allowed_actions:
            coach_prompt = append_action_instructions(
                coach_prompt, prompt.allowed_actions
            )
        else:
            coach_prompt = append_action_instructions(
                coach_prompt, ActionType.get_all_actions()
            )

        return coach_prompt, response_format
