from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from services.action_handler.models import SetCurrentIdentityParams


def set_current_identity(coach_state: CoachState, params: SetCurrentIdentityParams):
    """
    Set the current identity being refined in the Identity Refinement Phase.
    This function updates the current_identity field of the CoachState to point to the specified identity.
    """
    identity_id = params.identity_id
    
    try:
        identity = Identity.objects.get(id=identity_id)
        coach_state.current_identity = identity
        coach_state.save()
    except Identity.DoesNotExist:
        raise ValueError(f"Identity with ID {identity_id} does not exist") 