"""
build_scenario_template

Assemble the full scenario template dict from a user's current DB state.
"""

from apps.test_scenario.utils.build_user_template_section import (
    build_user_template_section,
)
from apps.test_scenario.utils.gather_actions_section import gather_actions_section
from apps.test_scenario.utils.gather_breaks_section import gather_breaks_section
from apps.test_scenario.utils.gather_chat_messages_section import (
    gather_chat_messages_section,
)
from apps.test_scenario.utils.gather_coach_state_section import (
    gather_coach_state_section,
)
from apps.test_scenario.utils.gather_identities_section import gather_identities_section
from apps.test_scenario.utils.gather_user_notes_section import gather_user_notes_section


def build_scenario_template(
    user,
    *,
    first_name: str = "",
    last_name: str = "",
) -> dict:
    """
    Assemble the full template dict from the user's current DB state.

    Gathers all relevant model data (CoachState, Identities, ChatMessages,
    UserNotes, Actions) and combines them into a single template dict suitable
    for storing on a TestScenario.

    Args:
        user: The User model instance whose session to capture.
        first_name: Override for the template user's first name.
        last_name: Override for the template user's last name.

    Returns:
        A template dict with a ``user`` key (always present) plus optional
        keys ``coach_state``, ``identities``, ``chat_messages``,
        ``original_message_mapping``, ``user_notes``, and ``actions``.
    """
    template: dict = {"user": build_user_template_section(user, first_name, last_name)}

    coach_state_section = gather_coach_state_section(user)
    if coach_state_section:
        template["coach_state"] = coach_state_section

    identities_section = gather_identities_section(user)
    if identities_section:
        template["identities"] = identities_section

    messages_section, original_mapping = gather_chat_messages_section(user)
    if messages_section:
        template["chat_messages"] = messages_section
    if original_mapping:
        template["original_message_mapping"] = original_mapping

    notes_section = gather_user_notes_section(user)
    if notes_section:
        template["user_notes"] = notes_section

    actions_section = gather_actions_section(user)
    if actions_section:
        template["actions"] = actions_section

    breaks_section = gather_breaks_section(user)
    if breaks_section:
        template["breaks"] = breaks_section

    return template
