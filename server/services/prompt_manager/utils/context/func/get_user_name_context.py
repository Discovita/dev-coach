from apps.coach_states.models import CoachState


def get_user_name_context(coach_state: CoachState) -> str:
    """
    Get the user's name context.

    The coach addresses the user by first name only, so this returns the
    user's first name (falling back to their email when no first name is set).
    """
    user = coach_state.user
    return user.first_name or user.email
