from apps.coach_states.models import CoachState


def get_who_you_are(coach_state: CoachState) -> str:
    """
    Get the user's "Who You Are" identities as a comma-separated string.
    """
    who_you_are = coach_state.who_you_are
    if not who_you_are:
        return "No Who You Are identities defined yet."
    return ", ".join(who_you_are)
