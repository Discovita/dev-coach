from typing import List, Dict

from apps.users.serializer import UserSerializer
from apps.coach_states.serializer import CoachStateSerializer
from apps.identities.serializer import IdentitySerializer
from apps.chat_messages.serializer import ChatMessageSerializer
from apps.user_notes.serializer import UserNoteSerializer


def validate_scenario_template(template: dict) -> List[Dict[str, str]]:
    """
    Validates a test scenario template against the current model schemas.

    Args:
        template (dict): The scenario template to validate. Should contain keys: 'user', 'coach_state', 'identities', 'chat_messages', 'user_notes'.

    Returns:
        List[Dict[str, str]]: A list of error dicts, each with 'section' and 'error' keys. Empty if valid.

    Example error:
        [{"section": "user", "error": "Missing required field: email"}]
    """
    errors = []

    # --- User section validation ---
    # TODO: Validate template['user'] using UserSerializer
    # If missing or invalid, append to errors

    # --- CoachState section validation ---
    # TODO: Validate template['coach_state'] using CoachStateSerializer

    # --- Identities section validation ---
    # TODO: Validate each identity in template['identities'] using IdentitySerializer

    # --- ChatMessages section validation ---
    # TODO: Validate each message in template['chat_messages'] using ChatMessageSerializer

    # --- UserNotes section validation ---
    # TODO: Validate each note in template['user_notes'] using UserNoteSerializer

    # --- Check for missing or null sections ---
    # TODO: Add logic to check for missing/null sections and append errors

    return errors 