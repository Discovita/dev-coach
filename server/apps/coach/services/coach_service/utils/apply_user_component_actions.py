"""
Utility to apply component actions that the user triggered.

When a user interacts with a component (like clicking a button), those actions
need to be processed and applied to the user's coach state.
"""
from typing import List, Optional
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from models.components.ComponentConfig import ComponentAction
from services.action_handler.handler import apply_component_actions


def apply_user_component_actions(
    coach_state: CoachState,
    user_chat_message: ChatMessage,
    request_component_actions: Optional[List],
) -> None:
    """
    Apply component actions that were triggered by user interactions.

    Component actions are things like "accept identity" or "combine identities"
    that happen when the user clicks buttons in the chat interface.

    Args:
        coach_state: The user's current coach state to update
        user_chat_message: The chat message that triggered these actions
        request_component_actions: List of actions to apply, or None if no actions
    """
    if not request_component_actions:
        return

    component_actions = [
        ComponentAction(**action) if isinstance(action, dict) else action
        for action in request_component_actions
    ]
    apply_component_actions(coach_state, component_actions, user_chat_message)

