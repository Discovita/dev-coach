from apps.user_notes.models import UserNote
from apps.coach_states.models import CoachState

def get_user_notes_context(coach_state: CoachState) -> str:
    """
    For a given coach_state, retrieve and format all associated UserNotes for the user.
    Returns a single string suitable for prompt context.
    """
    user_notes = UserNote.objects.filter(user=coach_state.user).order_by('created_at')
    return '; '.join([n.note for n in user_notes]) if user_notes else None 