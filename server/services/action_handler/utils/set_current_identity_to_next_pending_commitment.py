from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def set_current_identity_to_next_pending_commitment(coach_state: CoachState) -> None:
    """
    Set the current_identity to the next (oldest) identity that needs commitment.
    """
    # Find the next (oldest) identity that is NOT commitment_complete and NOT archived
    next_identity: Identity = (
        coach_state.user.identities.exclude(state=IdentityState.COMMITMENT_COMPLETE)
        .exclude(state=IdentityState.ARCHIVED)
        .order_by("created_at")
        .first()
    )

    if next_identity:
        log.debug(f"Setting current_identity to {next_identity.name}")
        coach_state.current_identity = next_identity
        coach_state.save()
    else:
        # No more identities to commit - clear current_identity
        log.warning("No more identities to commit - clearing current_identity")
        coach_state.current_identity = None
        coach_state.save()
