"""
Utility for appending action instructions to system messages for prompt generation.
Used by prompt_manager.manager and other prompt modules to add action instructions.
"""

import os
import time
from typing import List, Optional
from enums.action_type import ActionType
from services.action_handler.utils import get_action_instructions


def append_action_instructions(
    system_message: str,
    allowed_actions: Optional[List[ActionType]] = ActionType.get_all_actions(),
) -> str:
    """Append filtered action instructions to a system message."""
    
    action_instructions = get_action_instructions(allowed_actions)
    
    # Add cache busting to the action instructions section itself
    if "local" in os.getenv("DJANGO_SETTINGS_MODULE", ""):
        timestamp = int(time.time())
        action_instructions = f"# Action Instructions Cache bust: {timestamp}\n{action_instructions}"
    
    return f"{system_message}\n\n{action_instructions}"
