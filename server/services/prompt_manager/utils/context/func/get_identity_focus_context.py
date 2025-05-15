from apps.coach_states.models import CoachState
from enums.identity_category import IdentityCategory


def get_identity_focus_context(coach_state: CoachState) -> str:
    """
    Get the user's identity focus context as a human-readable label.
    This function retrieves the identity_focus value from the coach_state,
    converts it to an IdentityCategory enum member, and returns its label.
    """
    identity_focus_value = coach_state.identity_focus
    if identity_focus_value:
        try:
            identity_category_member = IdentityCategory.from_string(identity_focus_value)
            return identity_category_member.label
        except ValueError:
            # Fallback or error handling if the value is not a valid IdentityCategory
            # For now, returning the original value, but ideally log this situation
            return identity_focus_value
    return ""
