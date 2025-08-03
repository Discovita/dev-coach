from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import TransitionPhaseParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def transition_phase(coach_state: CoachState, params: TransitionPhaseParams, coach_message: ChatMessage) -> None:
    """
    Update the current_phase of the CoachState.
    """
    old_phase = coach_state.current_phase
    coach_state.current_phase = params.to_phase
    coach_state.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.TRANSITION_PHASE.value,
        parameters=params.model_dump(),
        result_summary=f"Transitioned from '{old_phase}' to '{params.to_phase}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
