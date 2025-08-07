from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UpdateIdentityNameParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def update_identity_name(coach_state: CoachState, params: UpdateIdentityNameParams, coach_message: ChatMessage):
    """
    Update only the name of an existing Identity for the user.
    """
    # Get the identity and update the name
    identity = Identity.objects.get(id=params.id, user=coach_state.user)
    old_name = identity.name
    identity.name = params.name
    identity.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.UPDATE_IDENTITY_NAME.value,
        parameters=params.model_dump(),
        result_summary=f"Updated identity name from '{old_name}' to '{identity.name}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
    
    return identity
