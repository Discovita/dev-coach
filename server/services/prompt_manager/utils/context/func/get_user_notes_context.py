from apps.user_notes.models import UserNote
from apps.coach_states.models import CoachState


def get_user_notes_context(coach_state: CoachState) -> str:
    """
    For a given coach_state, retrieve and format all associated UserNotes for the user.
    Formats these notes into a markdown-friendly string, with a heading.
    """
    user_notes = UserNote.objects.filter(user=coach_state.user).order_by("created_at")
    if user_notes:
        formatted_notes = []
        for i, note in enumerate(user_notes):
            formatted_notes.append(f"**{i+1}** (ID: {note.id}): {note.note}")
        notes_block = "\n".join(formatted_notes)
        return f"## User Notes\n\n{notes_block}\n"
    else:
        return f"## User Notes\n\nNo Notes Yet...\n"