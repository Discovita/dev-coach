from enums.context_keys import ContextKey
from apps.prompts.models import Prompt
from apps.coach_states.models import CoachState
from services.prompt_manager.models.prompt_context import PromptContext

# Add imports for other models as needed


def gather_prompt_context(prompt: Prompt, coach_state: CoachState) -> PromptContext:
    """
    Gather all required context values for a given prompt and coach state.
    """
    user = coach_state.user
    context_data = {}
    for key in prompt.required_context_keys:
        context_data[key] = get_context_value(key, coach_state)

    prompt_context_fields = {field: None for field in PromptContext.model_fields.keys()}
    for key, value in context_data.items():
        field_name = key.value if hasattr(key, "value") else str(key)
        if field_name in prompt_context_fields:
            prompt_context_fields[field_name] = value
    if prompt_context_fields["user_name"] is None:
        prompt_context_fields["user_name"] = user.get_full_name() or user.email
    if prompt_context_fields["number_of_identities"] is None:
        prompt_context_fields["number_of_identities"] = 0
    return PromptContext(**prompt_context_fields)


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
