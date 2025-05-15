from enums.context_keys import ContextKey
from apps.coach_states.models import CoachState


def get_context_value(key: ContextKey, coach_state: CoachState):
    """
    Given a ContextKey, gather the required value from the DB/models using coach_state.
    Returns a value suitable for the PromptContext field.
    """
    user = coach_state.user
    if key == ContextKey.USER_NAME:
        return user.get_full_name() or user.email
    elif key == ContextKey.RECENT_MESSAGES:
        messages = [
            str(msg) for msg in user.chat_messages.all().order_by("timestamp")[:5]
        ]
        return "\n".join(messages)
    elif key == ContextKey.IDENTITIES:
        identites = user.identities.all()

        return user.identities.all()
    elif key == ContextKey.NUMBER_OF_IDENTITIES:
        return user.identities.count()
    elif key == ContextKey.CURRENT_IDENTITY_DESCRIPTION:
        if coach_state.current_identity:
            return coach_state.current_identity.description
        return None
    # Add more context key handlers as needed
    else:
        # Handle unknown context keys
        raise ValueError(f"Unknown context key: {key}")
