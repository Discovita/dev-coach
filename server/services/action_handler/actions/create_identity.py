from apps.identities.models import Identity
from apps.coach_states.models import CoachState


def create_identity(coach_state: CoachState, params):
    """
    Create a new Identity and link it to the user.
    """
    return Identity.objects.create(
        user=coach_state.user,
        description=params["description"],
        state="proposed",
        notes=[params.get("note", "")],
        category=params["category"],
    )
