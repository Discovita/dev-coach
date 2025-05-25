from enums.context_keys import ContextKey
from apps.coach_states.models import CoachState

from services.prompt_manager.utils.context.func import (
    get_user_name_context,
    get_identities_context,
    get_number_of_identites_context,
    get_identity_focus_context,
    get_recent_messages_context,
    get_who_you_are,
    get_who_you_want_to_be,
)


def get_context_value(key: ContextKey, coach_state: CoachState):
    """
    Given a ContextKey, gather the required value from the DB/models using coach_state.
    Returns a value suitable for the PromptContext field.
    """
    if key == ContextKey.USER_NAME:
        return get_user_name_context(coach_state)
    elif key == ContextKey.RECENT_MESSAGES:
        return get_recent_messages_context(coach_state)
    elif key == ContextKey.IDENTITIES:
        return get_identities_context(coach_state)
    elif key == ContextKey.NUMBER_OF_IDENTITIES:
        return get_number_of_identites_context(coach_state)
    elif key == ContextKey.IDENTITY_FOCUS:
        return get_identity_focus_context(coach_state)
    elif key == ContextKey.WHO_YOU_ARE:
        return get_who_you_are(coach_state)
    elif key == ContextKey.WHO_YOU_WANT_TO_BE:
        return get_who_you_want_to_be(coach_state)
    # Add more context key handlers as needed
