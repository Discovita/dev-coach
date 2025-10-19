import os
import time
from apps.coach_states.models import CoachState
from services.prompt_manager.utils.context.func.get_user_notes_context import (
    get_user_notes_context,
)


def append_user_notes(prompt: str, coach_state: CoachState) -> str:
    """Append the user notes to a prompt"""
    
    notes = get_user_notes_context(coach_state=coach_state)
    
    # Add cache busting to the user notes section itself
    if "local" in os.getenv("DJANGO_SETTINGS_MODULE", ""):
        timestamp = int(time.time())
        notes = f"# Sentinel User Notes Cache bust: {timestamp}\n{notes}"
    
    return f"{prompt}\n\n{notes}"
