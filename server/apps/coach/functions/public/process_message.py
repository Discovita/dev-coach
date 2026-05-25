"""
process_message

Orchestrates the full flow of processing a user's chat message and generating
a coach response.

POST /api/v1/coach/process-message/
POST /api/v1/admin/coach/process-message-for-user/
"""

from typing import Any, Dict, List, Optional, Tuple

from apps.chat_messages.utils import add_chat_message, ensure_initial_message_exists
from apps.coach.utils import (
    apply_coach_response_actions,
    apply_user_component_actions,
    build_coach_prompt,
    build_coach_response_data,
    generate_coach_ai_response,
    get_recent_chat_messages_for_prompt,
)
from apps.coach_states.models import CoachState
from apps.users.models import User
from enums.ai import AIModel
from enums.message_role import MessageRole
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def process_message(
    user: User,
    message: Optional[str],
    request_component_actions: Optional[List],
    model: AIModel,
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Process a user's message and generate a coach response.

    Orchestration steps:
    1. Ensure the conversation has an initial message seeded.
    2. Save the user's message to chat history (skipped when `message is None`
       — the programmatic-only / action-only button case, e.g. the video
       Continue button).
    3. Apply any component actions the user triggered (e.g. accepting an
       identity, acknowledging a video, starting/ending a break). If any of
       them returns a `ComponentConfig`, it becomes the coach's response
       this turn and the LLM is skipped (skip-LLM-on-component rule).
    4. (LLM path only) Build the coach prompt for the current coaching phase.
    5. (LLM path only) Call the AI service to generate a structured response.
    6. (LLM path only) Save the coach's reply to chat history.
    7. (LLM path only) Apply any actions embedded in the coach response.
    8. Return the response data for the client.

    Args:
        user: The user sending the message.
        message: The user's message text. `None` means "no user message this
            turn" (programmatic-only, e.g. the video Continue button); no
            ChatMessage is written. `""` is treated as a real (empty) user
            message and IS saved.
        request_component_actions: Optional list of component actions from the
            request.
        model: The AI model to use for generation.

    Returns:
        Tuple of (success: bool, response_data: Dict, error_message: str)
        On success, response_data contains:
            - message: str — the coach's response text (empty when the
              skip-LLM rule fires)
            - final_prompt: str — the prompt used (empty when the LLM was
              skipped)
            - on_break: bool — derived from open Break rows
            - component: dict (optional) — UI component config if present
    """
    try:
        ensure_initial_message_exists(user)

        # Null-message contract: `message is None` is programmatic-only — the
        # request carries actions but no user-typed text. Skip the user
        # ChatMessage save in that case. Empty string `""` is a real (empty)
        # user message and DOES get saved.
        if message is None:
            user_chat_message = None
        else:
            user_chat_message = add_chat_message(user, message, MessageRole.USER)

        coach_state = CoachState.objects.get(user=user)

        user_component_config = apply_user_component_actions(
            coach_state, user_chat_message, request_component_actions
        )

        if user_component_config is not None:
            # Skip-LLM-on-component rule: a user action returned a
            # ComponentConfig (e.g. START_BREAK → SESSION_BREAK, END_BREAK
            # → SESSION_VIDEO intro). The component IS the coach's response
            # this turn — persist it as a coach ChatMessage and skip the
            # LLM call entirely.
            coach_message = add_chat_message(user, "", MessageRole.COACH)
            coach_message.component_config = user_component_config.model_dump()
            coach_message.save(update_fields=["component_config"])

            log.debug(
                f"Skip-LLM rule fired: user action returned "
                f"{user_component_config.component_type}"
            )

            on_break = user.breaks.filter(ended_at__isnull=True).exists()
            response_data = build_coach_response_data(
                coach_message="",
                final_prompt="",
                on_break=on_break,
                component_config=user_component_config,
            )
            return True, response_data, None

        coach_prompt, response_format = build_coach_prompt(user, model)

        # NOTE: Chat history is not passed separately — it is embedded directly
        # in the prompt by the PromptManager to include action context between messages.
        chat_history_for_prompt = get_recent_chat_messages_for_prompt(user)

        coach_response = generate_coach_ai_response(
            coach_prompt, chat_history_for_prompt, response_format, model
        )

        coach_message = add_chat_message(user, coach_response.message, MessageRole.COACH)

        updated_coach_state, component_config = apply_coach_response_actions(
            coach_state, coach_response, coach_message
        )

        log.debug(f"Updated Coach State: {updated_coach_state}")
        log.debug(f"Component Config: {component_config}")

        on_break = user.breaks.filter(ended_at__isnull=True).exists()

        response_data = build_coach_response_data(
            coach_response.message,
            coach_prompt,
            on_break,
            component_config,
        )
        return True, response_data, None

    except Exception as e:
        error_message = f"Error processing message for user {user.id}: {str(e)}"
        log.error(error_message, exc_info=True)
        return False, {}, error_message
