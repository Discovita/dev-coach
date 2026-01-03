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
from services.action_handler.utils import build_dynamic_response_format
from services.prompt_manager.utils import (
    prepend_system_context,
    prepend_user_notes,
    append_user_notes,
    append_action_instructions,
    append_recent_messages,
)
from services.logger import configure_logging
from enums.prompt_type import PromptType
from typing import Tuple, Union, Dict, Any
from pydantic import BaseModel

log = configure_logging(__name__, log_level="INFO")


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
    ) -> Tuple[str, Union[BaseModel, Dict[str, Any]]]:
        """
        Create a prompt for the chat endpoint using the user's context.
        Orchestrates context collection, prompt formatting, and action instructions.
        Args:
            user: The Django User instance for whom to build the prompt.
            version_override: Optional version number to override the default prompt version.
        Returns:
            Tuple[str, Type[BaseModel]]: prompt for the chat endpoint and the response format.
        """
        # 1. Retrieve the user's CoachState
        log.info(f"Creating chat prompt")
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
        prompt: Prompt = prompt_queryset.order_by("-version").first()
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

        # Prepend any current user notes
        coach_prompt = prepend_user_notes(coach_prompt, coach_state)

        coach_prompt = prepend_system_context(coach_prompt)
        # Append action instructions to the system message
        if prompt.allowed_actions:
            coach_prompt = append_action_instructions(
                coach_prompt, prompt.allowed_actions
            )
        else:
            log.warning(
                f"Prompt {prompt.name} has no allowed actions. Using all action instructions."
            )
            coach_prompt = append_action_instructions(
                coach_prompt, ActionType.get_all_actions()
            )
        log.debug(f"coach_prompt with actions: {coach_prompt}")

        # add the recent messages
        coach_prompt = append_recent_messages(coach_prompt, coach_state)

        return coach_prompt, response_format

    def create_sentinel_prompt(self, user: User, model: AIModel):
        """
        Build a prompt for the Sentinel LLM call using the latest active sentinel prompt from the database.
        - coach_state: the CoachState instance for the user
        """
        coach_state = CoachState.objects.get(user=user)
        # Fetch the latest active sentinel prompt
        prompt = (
            Prompt.objects.filter(prompt_type=PromptType.SENTINEL, is_active=True)
            .order_by("-version")
            .first()
        )
        log.info(f"Using Sentinel Prompt version: {prompt.version}")
        if not prompt:
            raise ValueError("No active Sentinel prompt found in the database.")
        # Gather context for the prompt
        prompt_context = gather_prompt_context(prompt, coach_state)
        provider = AIModel.get_provider(model)
        response_format_model = build_dynamic_response_format(prompt.allowed_actions)
        # Format the prompt for the provider
        sentinel_prompt, response_format = format_for_provider(
            prompt, prompt_context, provider, response_format_model
        )
        # Append any current user notes
        sentinel_prompt = append_user_notes(sentinel_prompt, coach_state)
        sentinel_prompt = append_action_instructions(
            sentinel_prompt, prompt.allowed_actions
        )
        # Save the prompt to a markdown file
        # with open("services/sentinel/most_recent_sentinel_prompt.md", "w", encoding="utf-8") as f:
        #     f.write(sentinel_prompt)
        return sentinel_prompt, response_format

    def create_image_generation_prompt(
        self,
        identity: "Identity",
        additional_prompt: str = "",
    ) -> str:
        """
        Create a prompt for identity image generation.

        Unlike chat prompts, this:
        - Takes an Identity directly (not from CoachState)
        - Returns just a string (no response_format model)
        - Uses a simpler context gathering flow (no actions, no message history)

        Args:
            identity: The Identity to generate an image for
            additional_prompt: Optional extra instructions from admin

        Returns:
            Formatted prompt string for Gemini image generation
        """
        from apps.identities.models import Identity
        from services.prompt_manager.utils.context.func import get_identity_context_for_image

        # Fetch the latest active image generation prompt
        prompt = (
            Prompt.objects.filter(
                prompt_type=PromptType.IMAGE_GENERATION,
                is_active=True,
            )
            .order_by("-version")
            .first()
        )

        if not prompt:
            raise ValueError("No active image generation prompt found in the database.")

        log.info(f"Using Image Generation Prompt version: {prompt.version}")

        # Gather identity context using our dedicated function
        identity_context = get_identity_context_for_image(identity)

        # Format the prompt template with context
        # The prompt body should have placeholders: {identity_context} and {additional_prompt}
        formatted_prompt = prompt.body.format(
            identity_context=identity_context,
            additional_prompt=additional_prompt or "None provided",
        )

        return formatted_prompt
