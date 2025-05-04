from apps.coach_states.models import CoachState

def transition_state(coach_state: CoachState, params):
    """
    Update the current_state of the CoachState.
    """
    coach_state.current_state = params["to_state"]
    coach_state.save() 