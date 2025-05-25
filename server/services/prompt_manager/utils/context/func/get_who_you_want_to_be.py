from apps.coach_states.models import CoachState


def get_who_you_want_to_be(coach_state: CoachState) -> str:
    """
    Get the user's "Who You Are" identities as a comma-separated string.
    """
    who_you_want_to_be = coach_state.who_you_want_to_be
    if not who_you_want_to_be:
        return "No Who You Want To Be identities defined yet."
    return ", ".join(who_you_want_to_be)
