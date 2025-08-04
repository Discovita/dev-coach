from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import SkipIdentityCategoryParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def skip_identity_category(coach_state: CoachState, params: SkipIdentityCategoryParams, coach_message: ChatMessage):
    """
    Add an identity category to the skipped_identity_categories list on a Users Coach State.
    """
    identity_category_to_skip = params.category
    if identity_category_to_skip in coach_state.skipped_identity_categories:
        return
    coach_state.skipped_identity_categories.append(identity_category_to_skip)
    coach_state.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SKIP_IDENTITY_CATEGORY.value,
        parameters=params.model_dump(),
        result_summary=f"Skipped identity category '{identity_category_to_skip}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
