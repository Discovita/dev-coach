from apps.prompts.models import Prompt
from apps.coach_states.models import CoachState
from services.prompt_manager.models.prompt_context import PromptContext
from services.prompt_manager.utils.context import get_context_value


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
