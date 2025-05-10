from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from services.action_handler.models import UpdateIdentityParams


def update_identity(coach_state: CoachState, params: UpdateIdentityParams):
    """
    Update the description of an existing Identity for the user.
    """
    Identity.objects.filter(id=params.id, user=coach_state.user).update(
        description=params.description
    )
