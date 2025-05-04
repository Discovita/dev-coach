from apps.identities.models import Identity
from apps.coach_states.models import CoachState

def update_identity(coach_state: CoachState, params):
    """
    Update the description of an existing Identity for the user.
    """
    Identity.objects.filter(id=params["id"], user=coach_state.user).update(
        description=params["description"]
    ) 