from typing import Optional

from django.conf import settings

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import CoachState
from apps.coach_states.utils.session_video_helpers import (
    intro_component_for,
    outro_component_for,
    should_emit_intro,
    should_emit_outro,
)
from enums.action_type import ActionType
from enums.coaching_phase import CoachingPhase, session_of
from enums.identity_state import IdentityState
from models.components.ComponentConfig import ComponentConfig
from services.action_handler.models import TransitionPhaseParams
from services.action_handler.utils import set_current_identity_to_next_pending
from services.action_handler.utils.update_all_user_identities_to_accepted_state import (
    update_all_user_identities_to_accepted_state,
)
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def transition_phase(
    coach_state: CoachState,
    params: TransitionPhaseParams,
    coach_message: ChatMessage,
) -> Optional[ComponentConfig]:
    """
    Update the current_phase of the CoachState.

    When `settings.COACHING_PHASE_VIDEOS_ENABLED` is True, also consult the
    SESSIONS map (via `should_emit_outro` / `should_emit_intro`) and attach
    a SESSION_VIDEO `ComponentConfig` to `coach_message` when the transition
    crosses a session boundary. Outro wins over intro when both would apply.
    Returns the attached component so the orchestrator can include it in
    the response payload alongside the LLM's transition text. Returns None
    when the flag is off or no video applies.
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
        set_current_identity_to_next_pending(
            coach_state, IdentityState.REFINEMENT_COMPLETE
        )

    if CoachingPhase.IDENTITY_COMMITMENT.value == params.to_phase:
        set_current_identity_to_next_pending(
            coach_state, IdentityState.COMMITMENT_COMPLETE
        )

    if CoachingPhase.I_AM_STATEMENT.value == params.to_phase:
        set_current_identity_to_next_pending(coach_state, IdentityState.I_AM_COMPLETE)

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

    if not settings.COACHING_PHASE_VIDEOS_ENABLED:
        return None

    component = _maybe_session_video_component(
        old_phase, params.to_phase, coach_state.shown_videos or []
    )
    if component is None:
        return None

    # Persist the component to the LLM's coach_message row so PR 11's
    # history serializer can render bracketed narration on the next turn
    # and so reloading the chat shows the card in its place.
    coach_message.component_config = component.model_dump()
    coach_message.save(update_fields=["component_config"])
    log.debug(
        f"Attached {component.component_type}({component.video_key}) to "
        f"coach_message {coach_message.id} for {old_phase_label} → {new_phase_label}"
    )
    return component


def _maybe_session_video_component(
    old_phase: str,
    new_phase: str,
    shown_videos,
) -> Optional[ComponentConfig]:
    """Return the SESSION_VIDEO component for this transition, or None.

    Outro wins over intro when both would apply (e.g. ANYTHING_MISSING →
    IDENTITY_COMMITMENT: outro of `refinement_session` fires; the
    `commitment_session` intro waits until after the break).
    """
    if should_emit_outro(old_phase):
        return outro_component_for(session_of(old_phase))
    if should_emit_intro(new_phase, shown_videos):
        return intro_component_for(session_of(new_phase))
    return None
