from apps.coach_states.models import CoachState
from services.action_handler.models import UnskipIdentityCategoryParams

def unskip_identity_category(coach_state: CoachState, params: UnskipIdentityCategoryParams):
    """
    Remove an identity category from the skipped_identity_categories list on a User's Coach State.
    """
    identity_category_to_unskip = params.category
    if identity_category_to_unskip in coach_state.skipped_identity_categories:
        coach_state.skipped_identity_categories.remove(identity_category_to_unskip)
        coach_state.save() 