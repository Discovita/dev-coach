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
    2. Log user_goals (as list and formatted)
    3. Log number_of_identities
    4. Log current_identity_description
    """
    # 1. Log user_name
    log.debug(f"USER_NAME: {getattr(prompt_context, 'user_name', None)}")
    # 2. Log user_goals
    log.debug(f"USER_GOALS: {getattr(prompt_context, 'user_goals', None)}")
    if hasattr(prompt_context, "format_goals"):
        log.debug(f"USER_GOALS (formatted): {prompt_context.format_goals()}")
    # 3. Log number_of_identities
    log.debug(
        f"NUMBER_OF_IDENTITIES: {getattr(prompt_context, 'number_of_identities', None)}"
    )
    # 4. Log current_identity_description
    log.debug(
        f"CURRENT_IDENTITY_DESCRIPTION: {getattr(prompt_context, 'current_identity_description', None)}"
    )
