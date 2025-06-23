from apps.user_notes.models import UserNote
from services.action_handler.models import UpdateUserNoteParams
from apps.coach_states.models import CoachState


def update_user_note(coach_state: CoachState, params: UpdateUserNoteParams):
    """
    Action handler to update one or more user notes by ID.
    For each item in params.notes:
      1. Fetch the UserNote by id and ensure it belongs to the current user.
      2. Update the note field with the new value.
      3. Save the UserNote.
    """
    for item in params.notes:
        try:
            user_note = UserNote.objects.get(id=item.id, user=coach_state.user)
            user_note.note = item.note.strip()
            user_note.save()
        except UserNote.DoesNotExist:
            # Optionally log or handle missing notes
            continue 