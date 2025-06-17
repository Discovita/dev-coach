from apps.user_notes.models import UserNote
from services.action_handler.models import AddUserNoteParams
from apps.coach_states.models import CoachState


def add_user_note(coach_state: CoachState, params: AddUserNoteParams):
    """
    Action handler to add a new note about the user.
    """
    UserNote.objects.create(user=coach_state.user, note=params.note)
