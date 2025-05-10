from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from services.action_handler.models import CreateIdentityParams


def create_identity(coach_state: CoachState, params: CreateIdentityParams):
    """
    Create a new Identity and link it to the user.
    """
    return Identity.objects.create(
        user=coach_state.user,
        description=params.description,
        state="proposed",
        notes=[params.note],
        category=params.category,
    )
