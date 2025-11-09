"""
Utility for prepending system context to system messages for prompt generation.
Used by prompt_manager.manager and other prompt modules to add system context from prompts/system_context.md.
"""

import os
import time
from apps.prompts.models import Prompt
from enums.coaching_phase import CoachingPhase
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def prepend_system_context(
    system_message: str,
) -> str:
    """
    Prepend the system context from the most recent version of the SYSTEM_CONTEXT to the given system message.
    """
    
    system_prompt_queryset = Prompt.objects.filter(
        coaching_phase=CoachingPhase.SYSTEM_CONTEXT,
        is_active=True,
    )
    system_context = system_prompt_queryset.order_by("-version").first()
    if system_context:
        context_body = system_context.body
        # Add cache busting to the system context section itself
        if "local" in os.getenv("DJANGO_SETTINGS_MODULE", ""):
            timestamp = int(time.time())
            context_body = f"# System Context Cache bust: {timestamp}\n{context_body}"
        result = f"{context_body}\n{system_message}"
    else:
        log.warning(
            f"System context not found for state {CoachingPhase.SYSTEM_CONTEXT}"
        )
        result = system_message
    
    return result
