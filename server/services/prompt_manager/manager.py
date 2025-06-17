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
from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
from services.prompt_manager import gather_prompt_context, format_for_provider
from services.action_handler.utils.dynamic_schema import build_dynamic_response_format
from services.prompt_manager.utils import (
    append_action_instructions,
    prepend_system_context,
    append_recent_messages,
)
from services.logger import configure_logging

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

    def create_sentinel_prompt(
        self,
        user_msg: ChatMessage,
        prev_coach_msg: ChatMessage,
        notes: list[UserNote],
    ):
        """
        Build a prompt for the Sentinel LLM call.
        - user: the User object
        - user_msg: the triggering ChatMessage (role=USER)
        - prev_coach_msg: the previous COACH ChatMessage (or None)
        - notes: list of UserNote objects
        """
        # Hardcoded template for Sentinel
        prompt = (
            "You are the Sentinel, an assistant that extracts and maintains important notes about the user.\n"
            "User message: {user_msg}\n"
            "Previous coach message: {prev_coach_msg}\n"
            "Current notes: {notes}\n"
            "Extract any new important information from the user message and update the notes list if needed. "
            "Return the updated notes as a concise, non-redundant list."
        ).format(
            user_msg=user_msg.content,
            prev_coach_msg=prev_coach_msg.content if prev_coach_msg else "None",
            notes='; '.join([n.note for n in notes]) if notes else "None"
        )
        allowed_actions = ["add_user_note"]
        response_format_model = build_dynamic_response_format(allowed_actions)

        # You can define a simple response format if needed
        response_format = {
            "notes": "list of strings (the updated notes)"
        }

        return prompt, response_format