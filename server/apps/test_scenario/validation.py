from typing import List, Dict

from apps.test_scenario.template_serializers import (
    TemplateUserSerializer,
    TemplateCoachStateSerializer,
    TemplateIdentitySerializer,
    TemplateChatMessageSerializer,
    TemplateUserNoteSerializer,
)
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")

def validate_scenario_template(template: dict) -> List[Dict[str, str]]:
    """
    Validates a test scenario template against the template serializers (creation schema).

    Args:
        template (dict): The scenario template to validate. Should contain keys: 'user', 'coach_state', 'identities', 'chat_messages', 'user_notes'.

    Returns:
        List[Dict[str, str]]: A list of error dicts, each with 'section' and 'error' keys. Empty if valid.

    Example error:
        [{"section": "user", "error": "Missing required field: email"}]
    """
    log.debug(f"[TestScenario.validation] Validating scenario template")
    errors = []

    # --- Helper for serializer errors ---
    def collect_serializer_errors(section, serializer_errors, index=None):
        for field, msgs in serializer_errors.items():
            if isinstance(msgs, dict):
                # Nested errors (shouldn't happen for our flat models)
                for subfield, submsgs in msgs.items():
                    for msg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                        loc = f"{section}{'['+str(index)+']' if index is not None else ''}" if subfield == 'non_field_errors' else f"{section}{'['+str(index)+']' if index is not None else ''}.{subfield}"
                        error_msg = f"{subfield}: {msg}" if subfield != 'non_field_errors' else str(msg)
                        errors.append({"section": loc, "error": error_msg})
            else:
                for msg in (msgs if isinstance(msgs, list) else [msgs]):
                    loc = f"{section}{'['+str(index)+']' if index is not None else ''}"
                    error_msg = f"{field}: {msg}" if field != 'non_field_errors' else str(msg)
                    errors.append({"section": loc, "error": error_msg})

    # --- Required sections ---
    required_sections = ["user"]
    for section in required_sections:
        if section not in template or template[section] is None:
            errors.append({"section": section, "error": f"Section '{section}' is missing or null."})

    # --- User section validation ---
    if "user" in template and template["user"] is not None:
        serializer = TemplateUserSerializer(data=template["user"])
        if not serializer.is_valid():
            collect_serializer_errors("user", serializer.errors)

    # --- CoachState section validation (optional) ---
    if "coach_state" in template and template["coach_state"] is not None:
        serializer = TemplateCoachStateSerializer(data=template["coach_state"])
        if not serializer.is_valid():
            collect_serializer_errors("coach_state", serializer.errors)

    # --- Identities section validation (optional) ---
    if "identities" in template and template["identities"] is not None:
        if not isinstance(template["identities"], list):
            errors.append({"section": "identities", "error": "Section 'identities' must be a list."})
        else:
            for idx, identity in enumerate(template["identities"]):
                serializer = TemplateIdentitySerializer(data=identity)
                if not serializer.is_valid():
                    collect_serializer_errors("identity", serializer.errors, index=idx)

    # --- ChatMessages section validation (optional) ---
    if "chat_messages" in template and template["chat_messages"] is not None:
        if not isinstance(template["chat_messages"], list):
            errors.append({"section": "chat_messages", "error": "Section 'chat_messages' must be a list."})
        else:
            for idx, msg in enumerate(template["chat_messages"]):
                serializer = TemplateChatMessageSerializer(data=msg)
                if not serializer.is_valid():
                    collect_serializer_errors("chat_message", serializer.errors, index=idx)

    # --- UserNotes section validation (optional) ---
    if "user_notes" in template and template["user_notes"] is not None:
        if not isinstance(template["user_notes"], list):
            errors.append({"section": "user_notes", "error": "Section 'user_notes' must be a list."})
        else:
            for idx, note in enumerate(template["user_notes"]):
                serializer = TemplateUserNoteSerializer(data=note)
                if not serializer.is_valid():
                    collect_serializer_errors("user_note", serializer.errors, index=idx)

    return errors 