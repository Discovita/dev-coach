from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from enums.identity_state import IdentityState
from services.action_handler.models import AcceptIdentityParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def accept_identity(coach_state: CoachState, params: AcceptIdentityParams, coach_message: ChatMessage):
    """
    Set the state of the specified Identity to 'accepted'.
    """
    Identity.objects.filter(id=params.id, user=coach_state.user).update(
        state=IdentityState.ACCEPTED
    )
    
    # Get the identity for logging
    identity = Identity.objects.get(id=params.id, user=coach_state.user)
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.ACCEPT_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=f"Accepted identity '{identity.name}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
