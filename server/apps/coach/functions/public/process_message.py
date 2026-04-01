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
    message: str,
    request_component_actions: Optional[List],
    model: AIModel,
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Process a user's message and generate a coach response.

    Orchestration steps:
    1. Ensure the conversation has an initial message seeded.
    2. Save the user's message to chat history.
    3. Apply any component actions the user triggered (e.g. accepting an identity).
    4. Build the coach prompt for the current coaching phase.
    5. Call the AI service to generate a structured response.
    6. Save the coach's reply to chat history.
    7. Apply any actions embedded in the coach response (e.g. create identity, transition phase).
    8. Return the response data for the client.

    Args:
        user: The user sending the message.
        message: The user's message text.
        request_component_actions: Optional list of component actions from the request.
        model: The AI model to use for generation.

    Returns:
        Tuple of (success: bool, response_data: Dict, error_message: str)
        On success, response_data contains:
            - message: str — the coach's response text
            - final_prompt: str — the prompt used (for debugging)
            - component: dict (optional) — UI component config if present
    """
    try:
        ensure_initial_message_exists(user)

        user_chat_message = add_chat_message(user, message, MessageRole.USER)

        coach_state = CoachState.objects.get(user=user)

        apply_user_component_actions(
            coach_state, user_chat_message, request_component_actions
        )

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

        response_data = build_coach_response_data(
            coach_response.message, coach_prompt, component_config
        )
        return True, response_data, None

    except Exception as e:
        error_message = f"Error processing message for user {user.id}: {str(e)}"
        log.error(error_message, exc_info=True)
        return False, {}, error_message
