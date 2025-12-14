from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from enums.identity_state import IdentityState
from services.action_handler.models import ArchiveIdentityParams
from enums.action_type import ActionType
from services.logger import configure_logging
from enums.coaching_phase import CoachingPhase
from services.action_handler.utils import set_current_identity_to_next_pending

log = configure_logging(__name__, log_level="INFO")


def archive_identity(
    coach_state: CoachState, params: ArchiveIdentityParams, coach_message: ChatMessage
):
    """
    Set the state of the specified Identity to 'archived'.
    Archived identities are excluded from active coaching workflows but remain in the database.
    """
    Identity.objects.filter(id=params.id, user=coach_state.user).update(
        state=IdentityState.ARCHIVED
    )

    # Get the identity for logging
    identity = Identity.objects.get(id=params.id, user=coach_state.user)

    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.ARCHIVE_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=f"Archived identity '{identity.name}'",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    # Set current_identity to the next pending identity based on current phase
    if coach_state.current_phase == CoachingPhase.IDENTITY_COMMITMENT.value:
        set_current_identity_to_next_pending(coach_state, IdentityState.COMMITMENT_COMPLETE)
