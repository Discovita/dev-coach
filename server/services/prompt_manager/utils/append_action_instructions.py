"""
Utility for appending action instructions to system messages for prompt generation.
Used by prompt_manager.manager and other prompt modules to add action instructions.
"""

from typing import List, Optional
from enums.action_type import ActionType
from services.action_handler.utils.action_instructions import get_action_instructions


def append_action_instructions(
    system_message: str,
    allowed_actions: Optional[List[ActionType]] = ActionType.get_all_actions(),
) -> str:
    """Append filtered action instructions to a system message.
    Args:
        system_message: The base system message string.
        allowed_actions: List of allowed ActionType enums (default: all actions).
    Returns:
        The system message with appended action instructions.
    """
    action_instructions = get_action_instructions(allowed_actions)
    return f"{system_message}\n\n{action_instructions}"
