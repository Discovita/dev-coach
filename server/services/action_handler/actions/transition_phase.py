from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import TransitionPhaseParams
from enums.action_type import ActionType
from enums.coaching_phase import CoachingPhase
from enums.identity_state import IdentityState
from services.logger import configure_logging
from services.action_handler.utils.update_all_user_identities_to_accepted_state import (
    update_all_user_identities_to_accepted_state,
)
from services.action_handler.utils import set_current_identity_to_next_pending

log = configure_logging(__name__, log_level="INFO")


def transition_phase(
    coach_state: CoachState, params: TransitionPhaseParams, coach_message: ChatMessage
) -> None:
    """
    Update the current_phase of the CoachState.
    """
    old_phase = coach_state.current_phase
    coach_state.current_phase = params.to_phase
    coach_state.save()

    # Get human-readable labels for the phases
    old_phase_label = CoachingPhase(old_phase).label if old_phase else "None"
    new_phase_label = CoachingPhase(params.to_phase).label

    # If moving into Identity Refinement, accept all current identities for this user and set the current identity to the next (should be first) pending refinement
    if CoachingPhase.IDENTITY_REFINEMENT.value == params.to_phase:
        update_all_user_identities_to_accepted_state(coach_state)
        set_current_identity_to_next_pending(coach_state, IdentityState.REFINEMENT_COMPLETE)

    if CoachingPhase.IDENTITY_COMMITMENT.value == params.to_phase:
        set_current_identity_to_next_pending(coach_state, IdentityState.COMMITMENT_COMPLETE)

    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.TRANSITION_PHASE.value,
        parameters=params.model_dump(),
        result_summary=f"Transitioned from '{old_phase_label}' to '{new_phase_label}'",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )
