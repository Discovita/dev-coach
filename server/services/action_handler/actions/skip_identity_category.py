from apps.coach_states.models import CoachState
from services.action_handler.models import SkipIdentityCategoryParams


def skip_identity_category(coach_state: CoachState, params: SkipIdentityCategoryParams):
    """
    Add an identity category to the skipped_identity_categories list on a Users Coach State.
    """
    identity_category_to_skip = params.category
    if identity_category_to_skip in coach_state.skipped_identity_categories:
        return
    coach_state.skipped_identity_categories.append(identity_category_to_skip)
    coach_state.save()
