from apps.prompts.models import Prompt
from apps.coach_states.models import CoachState
from services.prompt_manager.models.prompt_context import PromptContext
from services.prompt_manager.utils.context import get_context_value


def gather_prompt_context(prompt: Prompt, coach_state: CoachState) -> PromptContext:
    """
    This is the entry point for all of these functions in the context module.
    Gather all required context values for a given prompt and coach state.
    """
    context_data = {}
    for key in prompt.required_context_keys:
        context_data[key] = get_context_value(key, coach_state)

    prompt_context_fields = {field: None for field in PromptContext.model_fields.keys()}
    for key, value in context_data.items():
        field_name = key.value if hasattr(key, "value") else str(key)
        if field_name in prompt_context_fields:
            prompt_context_fields[field_name] = value
    return PromptContext(**prompt_context_fields)
