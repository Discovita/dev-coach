from apps.coach_states.models import CoachState
from services.action_handler.models import TransitionPhaseParams


def transition_state(coach_state: CoachState, params: TransitionPhaseParams) -> None:
    """
    Update the current_phase of the CoachState.
    """
    coach_state.current_phase = params.to_phase
    coach_state.save()
