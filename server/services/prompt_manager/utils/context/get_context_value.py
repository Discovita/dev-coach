from enums.context_keys import ContextKey
from apps.coach_states.models import CoachState

from services.prompt_manager.utils.context.func import (
    get_user_name_context,
    get_identities_context,
    get_number_of_identites_context,
)


def get_context_value(key: ContextKey, coach_state: CoachState):
    """
    Given a ContextKey, gather the required value from the DB/models using coach_state.
    Returns a value suitable for the PromptContext field.
    """
    user = coach_state.user
    if key == ContextKey.USER_NAME:
        return get_user_name_context(coach_state)
    elif key == ContextKey.RECENT_MESSAGES:
        messages = [
            str(msg) for msg in user.chat_messages.all().order_by("timestamp")[:5]
        ]
        return "\n".join(messages)
    elif key == ContextKey.IDENTITIES:
        return get_identities_context(coach_state)
    elif key == ContextKey.NUMBER_OF_IDENTITIES:
        return get_number_of_identites_context(coach_state)
    # Add more context key handlers as needed
