from typing import Dict, Any, Tuple, List, Optional
from apps.users.models import User
from enums.ai import AIModel
from apps.coach_states.models import CoachState
from apps.chat_messages.utils import add_chat_message
from enums.message_role import MessageRole
from services.logger import configure_logging
from apps.coach.services.coach_service.utils import (
    ensure_initial_message_exists,
    add_user_message_to_history,
    apply_user_component_actions,
    build_coach_prompt,
    get_recent_chat_messages_for_prompt,
    generate_coach_ai_response,
    apply_coach_response_actions,
    build_coach_response_data,
)

log = configure_logging(__name__, log_level="INFO")


def process_message(
    user: User,
    message: str,
    request_component_actions: Optional[List],
    model: AIModel,
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Process a message for a user and generate a coach response.

    This function orchestrates the entire flow of processing a user's message
    and generating an appropriate response from the coach.

    Returns:
        Tuple of (success: bool, response_data: Dict, error_message: str)
        On success, response_data contains:
            - message: str - The coach's response message
            - final_prompt: str - The final prompt used
            - component: dict (optional) - Component configuration if present
    """
    try:
        ensure_initial_message_exists(user)

        user_chat_message = add_chat_message(user, message, MessageRole.USER)

        coach_state = CoachState.objects.get(user=user)

        apply_user_component_actions(
            coach_state, user_chat_message, request_component_actions
        )

        coach_prompt, response_format = build_coach_prompt(user, model)

        # NOTE: The chat history is not part of the prompt; the messages are added as a separate parameter.
        chat_history_for_prompt = get_recent_chat_messages_for_prompt(user)

        coach_response = generate_coach_ai_response(
            coach_prompt, chat_history_for_prompt, response_format, model
        )
        coach_message = add_chat_message(
            user, coach_response.message, MessageRole.COACH
        )

        updated_coach_state, component_config = apply_coach_response_actions(
            coach_state, coach_response, coach_message
        )

        log.debug(f"Updated Coach State: {updated_coach_state}")
        log.debug(f"Component Config: {component_config}")

        response_data = build_coach_response_data(
            coach_response.message, coach_prompt, component_config
        )
        success = True
        error_message = None
        return success, response_data, error_message

    except Exception as e:
        success = False
        response_data = {}
        error_message = f"Error processing message for user {user.id}: {str(e)}"
        log.error(error_message, exc_info=True)
        return success, response_data, error_message
