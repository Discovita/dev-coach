from apps.coach_states.models import CoachState

def get_current_phase_context(coach_state: CoachState) -> str:
    """
    Returns the current coaching phase for the user as a string.
    """
    return coach_state.current_phase 