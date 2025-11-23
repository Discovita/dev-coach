from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import SetCurrentIdentityParams
from enums.action_type import ActionType
from enums.identity_state import IdentityState
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def set_current_identity(coach_state: CoachState, params: SetCurrentIdentityParams, coach_message: ChatMessage):
    """
    Set the current identity being refined in the Identity Refinement Phase.
    This function updates the current_identity field of the CoachState to point to the specified identity.
    """
    identity_id = params.identity_id
    
    try:
        identity = Identity.objects.get(id=identity_id)
        
        # Prevent setting archived identity as current
        if identity.state == IdentityState.ARCHIVED:
            raise ValueError(f"Cannot set archived identity as current: {identity_id}")
        
        coach_state.current_identity = identity
        coach_state.save()
        
        # Log the action with rich context
        Action.objects.create(
            user=coach_state.user,
            action_type=ActionType.SET_CURRENT_IDENTITY.value,
            parameters=params.model_dump(),
            result_summary=f"Set current identity to '{identity.name}'",
            coach_message=coach_message,
            test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
        )
    except Identity.DoesNotExist:
        raise ValueError(f"Identity with ID {identity_id} does not exist") 