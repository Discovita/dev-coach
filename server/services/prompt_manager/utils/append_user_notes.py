from apps.coach_states.models import CoachState
from services.prompt_manager.utils.context.func.get_user_notes_context import (
    get_user_notes_context,
)


def append_user_notes(prompt: str, coach_state: CoachState) -> str:
    """Append the user notes to a prompt"""
    notes = get_user_notes_context(coach_state=coach_state)
    return f"{prompt}\n\n{notes}"
