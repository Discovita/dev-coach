from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.prompt_manager.utils.format_identity_ids import format_identity_ids


def get_identity_ids_context(coach_state: CoachState) -> str:
    """
    Get all of the user's identities formatted as a simple name-ID mapping.
    Includes all identities (including archived) to handle references to identities
    that may no longer be in active lists.
    """
    user = coach_state.user
    identities: List[Identity] = user.identities.all()
    
    return format_identity_ids(identities)

