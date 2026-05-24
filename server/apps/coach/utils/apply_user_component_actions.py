"""
Utility to apply component actions that the user triggered.

When a user interacts with a component (like clicking a button), those actions
need to be processed and applied to the user's coach state.
"""

from typing import List, Optional

from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import CoachState
from models.components.ComponentConfig import ComponentAction, ComponentConfig
from services.action_handler.handler import apply_component_actions


def apply_user_component_actions(
    coach_state: CoachState,
    user_chat_message: ChatMessage,
    request_component_actions: Optional[List],
) -> Optional[ComponentConfig]:
    """
    Apply component actions that were triggered by user interactions.

    Component actions are things like "accept identity" or "combine identities"
    that happen when the user clicks buttons in the chat interface.

    Returns the ComponentConfig produced by the last action that returned one
    (e.g., START_BREAK → SESSION_BREAK, END_BREAK → SESSION_VIDEO for the
    next session's intro), or None. The orchestrator uses this to apply the
    skip-LLM-on-component rule wired up in PR 10.

    Args:
        coach_state: The user's current coach state to update
        user_chat_message: The chat message that triggered these actions
        request_component_actions: List of actions to apply, or None if no actions
    """
    if not request_component_actions:
        return None

    component_actions = [
        ComponentAction(**action) if isinstance(action, dict) else action
        for action in request_component_actions
    ]
    _, component_config = apply_component_actions(
        coach_state, component_actions, user_chat_message
    )
    return component_config
