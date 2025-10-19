from .append_action_instructions import append_action_instructions
from .append_recent_messages import append_recent_messages
from .append_user_notes import append_user_notes
from .context_logging import log_context_stats
from .format_for_provider import format_for_provider
from .format_identities import format_identities
from .format_identities_needing_refinement import format_identities_needing_refinement
from .format_skipped_categories import format_skipped_categories
from .prepend_system_context import prepend_system_context
from .prepend_user_notes import prepend_user_notes
from .context import *

__all__ = [
    "append_action_instructions",
    "append_recent_messages",
    "append_user_notes",
    "log_context_stats",
    "format_for_provider",
    "format_identities",
    "format_identities_needing_refinement",
    "format_skipped_categories",
    "gather_prompt_context",
    "prepend_system_context",
    "prepend_user_notes",
    # context functions
    "gather_prompt_context",
    "get_context_value",
    "get_user_name_context",
    "get_identities_context",
    "get_number_of_identites_context",
    "get_identity_focus_context",
    "get_recent_messages_context",
    "get_who_you_are",
    "get_who_you_want_to_be",
    "get_focused_identities_context",
    "get_user_notes_context",
    "get_current_message_context",
    "get_previous_message_context",
    "get_current_phase_context",
    "get_brainstorming_category_context",
    "get_current_identity_context",
    "get_asked_questions",
    "get_refinement_identities_context",
    "get_affirmation_identities_context",
    "get_visualization_identities_context",
]
