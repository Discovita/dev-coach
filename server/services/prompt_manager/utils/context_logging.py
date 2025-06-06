"""
Utility for logging prompt context statistics for debugging and development.
Used by prompt_manager.manager and other prompt modules to log context details.
"""

from services.prompt_manager.models import PromptContext
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def log_context_stats(prompt_context: PromptContext):
    """
    Log a summary of the current prompt context for debugging.
    Logs all fields from PromptContext, matching the context keys in ContextKey.
    Step-by-step:
    1. Log user_name
    3. Log number_of_identities
    """
    # 1. Log user_name
    log.debug(f"USER_NAME: {getattr(prompt_context, 'user_name', None)}")
    # 3. Log number_of_identities
    log.debug(
        f"NUMBER_OF_IDENTITIES: {getattr(prompt_context, 'number_of_identities', None)}"
    )
    log.debug(f"FOCUSED_IDENTITIES: {getattr(prompt_context, 'focused_identities', None)}")
