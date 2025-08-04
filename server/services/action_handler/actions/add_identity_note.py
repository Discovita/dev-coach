from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import AddIdentityNoteParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def add_identity_note(
    coach_state: CoachState, params: AddIdentityNoteParams, coach_message: ChatMessage
):
    """
    Append a note to the notes list of the specified Identity.
    """
    identity = Identity.objects.get(id=params.id, user=coach_state.user)
    notes = identity.notes or []
    notes.append(params.note)
    identity.notes = notes
    identity.save()

    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.ADD_IDENTITY_NOTE.value,
        parameters=params.model_dump(),
        result_summary=f"Added note to identity '{identity.name}': {params.note}",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )
