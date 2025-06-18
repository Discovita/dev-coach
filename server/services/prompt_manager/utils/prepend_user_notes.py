from apps.coach_states.models import CoachState
from services.prompt_manager.utils.context.func.get_user_notes_context import get_user_notes_context


def prepend_user_notes(prompt: str, coach_state: CoachState) -> str:
    """Prepend the user notes to a prompt"""
    notes = get_user_notes_context(coach_state=coach_state)
    return f"{notes}\n\n{prompt}"
