from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState
from services.prompt_manager.utils.format_identities import format_identities

def get_focused_identities_context(coach_state: CoachState) -> str:
    """
    Return the user's identities that match the current identity_focus (category).
    If the category is in skipped categories and there are no identities, return a skipped message.
    """
    user = coach_state.user
    # Exclude archived identities from focused identities
    identities: List[Identity] = user.identities.exclude(state=IdentityState.ARCHIVED)
    focus = coach_state.identity_focus
    if not focus:
        return "No identity focus set."
    try:
        focus_category = IdentityCategory.from_string(focus)
    except Exception:
        return f"Invalid identity focus: {focus}"
    focused = [i for i in identities if i.category == focus_category.value]
    skipped = coach_state.skipped_identity_categories or []
    if not focused:
        if focus_category.value in skipped:
            return f"The category '{focus_category.label}' was skipped."
        return f"No identities found for focus: {focus_category.label}"
    return format_identities(focused) 