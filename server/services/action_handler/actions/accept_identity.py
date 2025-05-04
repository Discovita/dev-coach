from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from enums.identity_state import IdentityState

def accept_identity(coach_state: CoachState, params):
    """
    Set the state of the specified Identity to 'accepted'.
    """
    Identity.objects.filter(id=params["id"], user=coach_state.user).update(
        state=IdentityState.ACCEPTED
    ) 