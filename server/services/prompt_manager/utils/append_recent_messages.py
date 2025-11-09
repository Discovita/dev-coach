"""
Utility for appending action instructions to system messages for prompt generation.
Used by prompt_manager.manager and other prompt modules to add action instructions.
"""

import os
import time
from apps.coach_states.models import CoachState
from services.prompt_manager.utils.context.func.get_recent_messages_context import (
    get_recent_messages_context,
)


def append_recent_messages(system_message: str, coach_state: CoachState) -> str:
    """Append filtered action instructions to a system message."""
    
    recent_messages = get_recent_messages_context(coach_state=coach_state)
    
    # Add cache busting to the recent messages section itself
    if "local" in os.getenv("DJANGO_SETTINGS_MODULE", ""):
        timestamp = int(time.time())
        recent_messages = f"# Recent Messages Cache bust: {timestamp}\n{recent_messages}"
    
    return f"{system_message}\n\n{recent_messages}"
