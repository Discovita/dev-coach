from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from services.prompt_manager.utils.format_identities import format_identities
from services.prompt_manager.utils.format_skipped_categories import (
    format_skipped_categories,
)


def get_identities_context(coach_state: CoachState) -> str:
    """
    Get the user's identities and format them for insertion into a prompt.
    Each identity is formatted into a markdown-compatible string.
    Also includes a section listing skipped identity categories (if any).
    """
    user = coach_state.user
    identities: List[Identity] = user.identities.all()
    skipped = coach_state.skipped_identity_categories or []

    identities_section = format_identities(identities)
    skipped_section = format_skipped_categories(skipped)

    return identities_section + skipped_section
