from apps.coach_states.models import CoachState


def get_number_of_identites_context(coach_state: CoachState) -> str:
    """
    Get the number of identities that the User has created.
    """
    user = coach_state.user
    return user.identities.count()
