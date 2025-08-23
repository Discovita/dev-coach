from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.prompt_manager.utils.format_identities import format_identities


def get_visualization_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT visualization_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need visualization.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to be visualized, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT visualization_complete
    identities: List[Identity] = user.identities.exclude(state=IdentityState.VISUALIZATION_COMPLETE)

    # Check if there are any identities left to visualize
    if identities.count() == 0:
        return "No more identities left to visualize - time to move to the next phase!"
    
    return format_identities(identities)
