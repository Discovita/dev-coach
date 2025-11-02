"""
Utility to apply actions from the coach's response.

When the coach responds, it may include actions like creating an identity
or transitioning to a new phase. This function processes those actions.
"""
from typing import Tuple, Optional
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from models.CoachChatResponse import CoachChatResponse
from models.components.ComponentConfig import ComponentConfig
from services.action_handler.handler import apply_coach_actions


def apply_coach_response_actions(
    coach_state: CoachState,
    coach_response: CoachChatResponse,
    coach_message: ChatMessage,
) -> Tuple[CoachState, Optional[ComponentConfig]]:
    """
    Apply actions specified in the coach's response.

    The coach's response may include actions like:
    - Creating a new identity
    - Transitioning to a new coaching phase
    - Showing a component for user interaction

    Args:
        coach_state: The user's current coach state to update
        coach_response: The response from the AI containing actions
        coach_message: The chat message that contains the coach's response

    Returns:
        Tuple of (updated_coach_state, component_config)
        - updated_coach_state: The coach state after applying actions
        - component_config: Optional component configuration if the coach wants to show a UI component
    """
    return apply_coach_actions(coach_state, coach_response, coach_message)

