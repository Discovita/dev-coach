from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.prompt_manager.utils.format_identities import format_identities


def get_refinement_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT refinement_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need refinement.
    Each Identity is formatted into a markdown-compatible string.
    Also includes a section listing skipped identity categories (if any).
    """
    user = coach_state.user
    # Filter to only show identities that are NOT refinement_complete
    identities: List[Identity] = user.identities.exclude(state=IdentityState.REFINEMENT_COMPLETE)

    return format_identities(identities)
