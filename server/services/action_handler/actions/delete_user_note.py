from apps.user_notes.models import UserNote
from services.action_handler.models import DeleteUserNoteParams
from apps.coach_states.models import CoachState


def delete_user_note(coach_state: CoachState, params: DeleteUserNoteParams):
    """
    Action handler to delete one or more user notes by ID.
    For each id in params.ids:
      1. Fetch the UserNote by id and ensure it belongs to the current user.
      2. Delete the UserNote.
    """
    for note_id in params.ids:
        try:
            user_note = UserNote.objects.get(id=note_id, user=coach_state.user)
            user_note.delete()
        except UserNote.DoesNotExist:
            # Optionally log or handle missing notes
            continue 