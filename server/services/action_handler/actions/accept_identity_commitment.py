from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from enums.identity_state import IdentityState
from services.action_handler.models import AcceptIdentityCommitmentParams
from enums.action_type import ActionType
from services.logger import configure_logging
from services.action_handler.utils import set_current_identity_to_next_pending

log = configure_logging(__name__, log_level="INFO")


def accept_identity_commitment(
    coach_state: CoachState, params: AcceptIdentityCommitmentParams, coach_message: ChatMessage
):
    """
    Set the state of the specified Identity to 'commitment_complete'.
    """
    Identity.objects.filter(id=params.id, user=coach_state.user).update(
        state=IdentityState.COMMITMENT_COMPLETE
    )
    
    # Get the identity for logging
    identity = Identity.objects.get(id=params.id, user=coach_state.user)
    
    set_current_identity_to_next_pending(coach_state, IdentityState.COMMITMENT_COMPLETE)
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.ACCEPT_IDENTITY_COMMITMENT.value,
        parameters=params.model_dump(),
        result_summary=f"Accepted commitment for identity '{identity.name}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )

