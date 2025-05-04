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
    3. Log num_identities
    4. Log current_identity_description
    5. Log identities_summary (as list and formatted)
    6. Log phase
    7. Log recent_messages (as list and formatted)
    8. Log a summary line for quick inspection
    """
    # 1. Log user_name
    log.debug(f"USER_NAME: {getattr(prompt_context, 'user_name', None)}")
    # 2. Log user_goals
    log.debug(f"USER_GOALS: {getattr(prompt_context, 'user_goals', None)}")
    if hasattr(prompt_context, 'format_goals'):
        log.debug(f"USER_GOALS (formatted): {prompt_context.format_goals()}")
    # 3. Log num_identities
    log.debug(f"NUMBER_OF_IDENTITIES: {getattr(prompt_context, 'num_identities', None)}")
    # 4. Log current_identity_description
    log.debug(f"CURRENT_IDENTITY_DESCRIPTION: {getattr(prompt_context, 'current_identity_description', None)}")
    # 5. Log identities_summary
    log.debug(f"IDENTITIES_SUMMARY: {getattr(prompt_context, 'identities_summary', None)}")
    if hasattr(prompt_context, 'format_identities'):
        log.debug(f"IDENTITIES_SUMMARY (formatted):\n{prompt_context.format_identities()}")
    # 6. Log phase
    log.debug(f"PHASE: {getattr(prompt_context, 'phase', None)}")
    # 8. Log a summary line for quick inspection
    if hasattr(prompt_context, 'user_summary'):
        log.info(f"USER SUMMARY: {prompt_context.user_summary()}")