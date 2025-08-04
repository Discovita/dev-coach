from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UnskipIdentityCategoryParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def unskip_identity_category(coach_state: CoachState, params: UnskipIdentityCategoryParams, coach_message: ChatMessage):
    """
    Remove an identity category from the skipped_identity_categories list on a User's Coach State.
    """
    identity_category_to_unskip = params.category
    if identity_category_to_unskip in coach_state.skipped_identity_categories:
        coach_state.skipped_identity_categories.remove(identity_category_to_unskip)
        coach_state.save()
        
        # Log the action with rich context
        Action.objects.create(
            user=coach_state.user,
            action_type=ActionType.UNSKIP_IDENTITY_CATEGORY.value,
            parameters=params.model_dump(),
            result_summary=f"Unskipped identity category '{identity_category_to_unskip}'",
            coach_message=coach_message,
            test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
        ) 