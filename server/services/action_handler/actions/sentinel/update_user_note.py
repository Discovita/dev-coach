from apps.user_notes.models import UserNote
from services.action_handler.models import UpdateUserNoteParams
from apps.coach_states.models import CoachState


# NOTE: For now, this function does not log actions to the Action table.
# Since these actions are performed by the Sentinel only, these actions don't belong with the "Coach" actions
def update_user_note(coach_state: CoachState, params: UpdateUserNoteParams):
    """
    Action handler to update one or more user notes by ID.
    """
    for item in params.notes:
        try:
            user_note = UserNote.objects.get(id=item.id, user=coach_state.user)
            user_note.note = item.note.strip()
            user_note.save()
        except UserNote.DoesNotExist:
            # Optionally log or handle missing notes
            continue
