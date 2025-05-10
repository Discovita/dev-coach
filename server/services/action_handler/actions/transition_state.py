from apps.coach_states.models import CoachState
from services.action_handler.models import TransitionStateParams


def transition_state(coach_state: CoachState, params: TransitionStateParams) -> None:
    """
    Update the current_state of the CoachState.
    """
    coach_state.current_state = params.to_state
    coach_state.save()
