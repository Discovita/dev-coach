from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UpdateIdentityVisualizationParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def update_identity_visualization(coach_state: CoachState, params: UpdateIdentityVisualizationParams, coach_message: ChatMessage):
    """
    Update only the visualization of an existing Identity for the user.
    Step-by-step:
    1. Find the identity by ID and user
    2. Update the visualization field
    3. Log the action with details
    """
    # Get the identity and update the visualization
    identity = Identity.objects.get(id=params.id, user=coach_state.user)
    identity.visualization = params.visualization
    identity.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.UPDATE_IDENTITY_VISUALIZATION.value,
        parameters=params.model_dump(),
        result_summary=f"Updated identity '{identity.name}' visualization",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
    
    return identity
