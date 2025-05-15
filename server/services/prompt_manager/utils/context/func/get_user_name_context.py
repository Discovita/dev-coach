from apps.coach_states.models import CoachState


def get_user_name_context(coach_state: CoachState) -> str:
    """
    Get the user's name context.
    """
    user = coach_state.user
    return user.get_full_name() or user.email
