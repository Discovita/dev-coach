from enums.context_keys import ContextKey
from apps.chat_messages.models import ChatMessage
from apps.prompts.models import Prompt
from apps.coach_states.models import CoachState
from services.prompt_manager.models.prompt_context import PromptContext, IdentitySummary

# Add imports for other models as needed


def gather_prompt_context(prompt: Prompt, coach_state: CoachState) -> PromptContext:
    """
    Gather all required context values for a given prompt and coach state.
    Returns a PromptContext Pydantic model instance.
    Args:
        prompt: The Prompt instance specifying required context keys.
        coach_state: The CoachState instance for the user.
    Returns:
        PromptContext: Context object for prompt formatting.
    """
    user = coach_state.user
    context_data = {}
    for key in prompt.required_context_keys:
        context_data[key] = get_context_value(key, coach_state)
    # Map context_data to PromptContext fields
    return PromptContext(
        user_name=context_data.get(ContextKey.USER_NAME, user.get_full_name() or user.email),
        user_goals=context_data.get(ContextKey.USER_GOALS, []),
        num_identities=context_data.get(ContextKey.NUMBER_OF_IDENTITIES, 0),
        current_identity_description=context_data.get(ContextKey.CURRENT_IDENTITY_DESCRIPTION),
        identities_summary=context_data.get(ContextKey.IDENTITIES_SUMMARY, []),
        phase=context_data.get(ContextKey.PHASE, str(coach_state.current_state)),
    )


def get_context_value(key: ContextKey, coach_state: CoachState):
    """
    Given a ContextKey, gather the required value from the DB/models using coach_state.
    Returns a value suitable for the PromptContext field.
    """
    user = coach_state.user
    if key == ContextKey.USER_NAME:
        return user.get_full_name() or user.email
    elif key == ContextKey.USER_GOALS:
        # Example: get goals from coach_state metadata or a goals field
        return coach_state.goals
    # TODO: Implement other context keys as needed
    elif key == ContextKey.NUMBER_OF_IDENTITIES:
        return user.identities.count()
    elif key == ContextKey.CURRENT_IDENTITY_DESCRIPTION:
        if coach_state.current_identity:
            return coach_state.current_identity.description
        return None
    elif key == ContextKey.IDENTITIES_SUMMARY:
        # Return a list of IdentitySummary models
        return [
            IdentitySummary(
                id=str(identity.id),
                description=identity.description,
                state=identity.state,
            )
            for identity in user.identities.all()
        ]
    elif key == ContextKey.PHASE:
        return str(coach_state.current_state)
    # Add more context key handlers as needed
    else:
        # Handle unknown context keys
        raise ValueError(f"Unknown context key: {key}")
