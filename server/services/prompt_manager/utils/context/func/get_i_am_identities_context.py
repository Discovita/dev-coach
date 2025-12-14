from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.prompt_manager.utils.format_identities import format_identities


def get_i_am_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT i_am_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need an 'I Am' statement.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to be affirmed, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT i_am_complete and NOT archived
    identities: List[Identity] = user.identities.exclude(state=IdentityState.I_AM_COMPLETE).exclude(state=IdentityState.ARCHIVED)

    # Check if there are any identities left to affirm
    if identities.count() == 0:
        return "No more identities left to affirm - time to move to the Identity Visualization phase"
    
    return format_identities(identities)
