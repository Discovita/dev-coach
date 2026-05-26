"""
instantiate_test_scenario

Instantiate a test scenario by creating all DB objects from its template.

See: apps/test_scenario/functions/__init__.py
"""

from apps.test_scenario.utils.create_scenario_actions import create_scenario_actions
from apps.test_scenario.utils.create_scenario_breaks import create_scenario_breaks
from apps.test_scenario.utils.create_scenario_chat_messages import (
    create_scenario_chat_messages,
)
from apps.test_scenario.utils.create_scenario_coach_state import (
    create_scenario_coach_state,
)
from apps.test_scenario.utils.create_scenario_identities import (
    create_scenario_identities,
)
from apps.test_scenario.utils.create_scenario_user import create_scenario_user
from apps.test_scenario.utils.create_scenario_user_notes import (
    create_scenario_user_notes,
)
from services.logger import configure_logging

log = configure_logging(__name__)


def instantiate_test_scenario(
    scenario,
    *,
    create_user: bool = True,
    create_chat_messages: bool = False,
    create_identities: bool = False,
    create_coach_state: bool = False,
    create_user_notes: bool = False,
    create_actions: bool = False,
    create_breaks: bool = False,
) -> dict:
    """
    Create all DB objects described by *scenario.template*.

    Deletes any existing objects for this scenario before re-creating them,
    so calling this function is idempotent.

    Args:
        scenario: The TestScenario instance to instantiate.
        create_user: Whether to create the test user.
        create_chat_messages: Whether to create chat messages.
        create_identities: Whether to create identities.
        create_coach_state: Whether to apply coach state from the template.
        create_user_notes: Whether to create user notes.
        create_actions: Whether to create actions.
        create_breaks: Whether to create Coaching Phase Videos Break rows.

    Returns:
        A dict with keys ``user``, ``coach_state``, and ``email``.
    """
    template = scenario.template
    created_user = None
    created_coach_state = None
    unique_email = None

    if create_user:
        created_user, unique_email = create_scenario_user(scenario, template)

    created_identities = {}
    if create_identities and template.get("identities"):
        created_identities = create_scenario_identities(
            scenario, template, created_user
        )

    if create_coach_state and template.get("coach_state") and created_user:
        created_coach_state = create_scenario_coach_state(
            scenario, template, created_user, created_identities
        )

    original_to_new_msg = {}
    if create_chat_messages and template.get("chat_messages") and created_user:
        original_to_new_msg = create_scenario_chat_messages(
            scenario, template, created_user
        )

    if create_user_notes and template.get("user_notes") and created_user:
        create_scenario_user_notes(scenario, template, created_user)

    if create_actions and template.get("actions") and created_user:
        create_scenario_actions(scenario, template, created_user, original_to_new_msg)

    # Coaching Phase Videos: recreate Break rows after chat messages so
    # the `coach_message` FK can resolve against the just-created messages.
    if create_breaks and template.get("breaks") and created_user:
        create_scenario_breaks(scenario, template, created_user, original_to_new_msg)

    return {
        "user": created_user,
        "coach_state": created_coach_state,
        "email": unique_email,
    }
