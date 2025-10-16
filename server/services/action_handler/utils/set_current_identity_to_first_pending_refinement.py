from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState


def set_current_identity_to_first_pending_refinement(coach_state: CoachState) -> None:
    """
    Set the current_identity to the first (oldest) identity that needs refinement.
    This is used when transitioning to the Identity Refinement phase to automatically
    start with the first identity that hasn't been marked as refinement_complete.
    """
    # Find the first (oldest) identity that is NOT refinement_complete
    first_identity: Identity = coach_state.user.identities.exclude(
        state=IdentityState.REFINEMENT_COMPLETE
    ).order_by('created_at').first()
    
    if first_identity:
        coach_state.current_identity = first_identity
        coach_state.save()
