from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def set_current_identity_to_next_pending(
    coach_state: CoachState, complete_state: IdentityState
) -> None:
    """
    Set the current_identity to the next (oldest) identity that hasn't reached the specified complete state.
    
    This generic function finds identities that are:
    - NOT in the specified complete_state
    - NOT archived
    - Ordered by created_at (oldest first)
    
    Args:
        coach_state: The CoachState to update
        complete_state: The IdentityState that represents "complete" for this phase
                       (e.g., IdentityState.REFINEMENT_COMPLETE, IdentityState.COMMITMENT_COMPLETE)
    
    Examples:
        # For refinement phase
        set_current_identity_to_next_pending(coach_state, IdentityState.REFINEMENT_COMPLETE)
        
        # For commitment phase
        set_current_identity_to_next_pending(coach_state, IdentityState.COMMITMENT_COMPLETE)
        
        # For I Am Statement phase
        set_current_identity_to_next_pending(coach_state, IdentityState.I_AM_COMPLETE)
    """
    # Find the next (oldest) identity that is NOT in the complete state and NOT archived
    next_identity: Identity = (
        coach_state.user.identities.exclude(state=complete_state)
        .exclude(state=IdentityState.ARCHIVED)
        .order_by("created_at")
        .first()
    )

    if next_identity:
        log.debug(
            f"Setting current_identity to {next_identity.name} "
            f"(excluding {complete_state.label})"
        )
        coach_state.current_identity = next_identity
        coach_state.save()
    else:
        # No more identities pending - clear current_identity
        log.debug(
            f"No more identities pending (excluding {complete_state.label}) - "
            "clearing current_identity"
        )
        coach_state.current_identity = None
        coach_state.save()

