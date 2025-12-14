from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.prompt_manager.utils.format_identities_needing_commitment import format_identities_needing_commitment


def get_commitment_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT commitment_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need commitment.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to be committed to, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT commitment_complete and NOT archived, sorted by oldest first
    identities: List[Identity] = user.identities.exclude(state=IdentityState.COMMITMENT_COMPLETE).exclude(state=IdentityState.ARCHIVED).order_by('created_at')

    # Check if there are any identities left to commit to
    if identities.count() == 0:
        return "No more identities left to commit to - time to move to the next phase!"
    
    return format_identities_needing_commitment(identities)

