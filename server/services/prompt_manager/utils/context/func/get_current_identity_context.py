from apps.coach_states.models import CoachState


def get_current_identity_context(coach_state: CoachState) -> str:
    """
    Get the current identity being refined in the Identity Refinement Phase.
    Returns the name of the current identity if one is set, otherwise returns None.
    """
    if coach_state.current_identity:
        return coach_state.current_identity.name
    return None 