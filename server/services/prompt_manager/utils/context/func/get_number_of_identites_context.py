from apps.coach_states.models import CoachState
from enums.identity_state import IdentityState


def get_number_of_identites_context(coach_state: CoachState) -> int:
    """
    Get the number of identities that the User has created (excluding archived).
    """
    user = coach_state.user
    return user.identities.exclude(state=IdentityState.ARCHIVED).count()
