"""
Template validation logic for test scenario templates.

See: apps/test_scenario/utils/__init__.py
"""

from apps.test_scenario.serializers import (
    TemplateActionSerializer,
    TemplateChatMessageSerializer,
    TemplateCoachStateSerializer,
    TemplateIdentitySerializer,
    TemplateUserNoteSerializer,
    TemplateUserSerializer,
)


def validate_scenario_template(template: dict) -> list[dict[str, str]]:
    """
    Validate a test scenario template against the template serializers.

    Args:
        template: The scenario template dict. Expected keys include ``user``
            (required), and optionally ``coach_state``, ``identities``,
            ``chat_messages``, ``user_notes``, ``actions``.

    Returns:
        A list of error dicts, each with ``section`` and ``error`` keys.
        Empty if the template is valid.
    """
    errors: list[dict[str, str]] = []

    def _collect_errors(section, serializer_errors, index=None):
        """Flatten DRF validation errors into a uniform list."""
        for field, msgs in serializer_errors.items():
            if isinstance(msgs, dict):
                for subfield, submsgs in msgs.items():
                    for msg in submsgs if isinstance(submsgs, list) else [submsgs]:
                        suffix = f"[{index}]" if index is not None else ""
                        loc = (
                            f"{section}{suffix}"
                            if subfield == "non_field_errors"
                            else f"{section}{suffix}.{subfield}"
                        )
                        error_msg = (
                            f"{subfield}: {msg}"
                            if subfield != "non_field_errors"
                            else str(msg)
                        )
                        errors.append({"section": loc, "error": error_msg})
            else:
                for msg in msgs if isinstance(msgs, list) else [msgs]:
                    suffix = f"[{index}]" if index is not None else ""
                    loc = f"{section}{suffix}"
                    error_msg = (
                        f"{field}: {msg}" if field != "non_field_errors" else str(msg)
                    )
                    errors.append({"section": loc, "error": error_msg})

    # Required sections
    if "user" not in template or template["user"] is None:
        errors.append(
            {"section": "user", "error": "Section 'user' is missing or null."}
        )

    # Validate each section with its corresponding serializer
    _SINGLE_SECTIONS = {
        "user": TemplateUserSerializer,
        "coach_state": TemplateCoachStateSerializer,
    }
    _LIST_SECTIONS = {
        "identities": ("identity", TemplateIdentitySerializer),
        "chat_messages": ("chat_message", TemplateChatMessageSerializer),
        "user_notes": ("user_note", TemplateUserNoteSerializer),
        "actions": ("action", TemplateActionSerializer),
    }

    for key, serializer_cls in _SINGLE_SECTIONS.items():
        if key in template and template[key] is not None:
            ser = serializer_cls(data=template[key])
            if not ser.is_valid():
                _collect_errors(key, ser.errors)

    for key, (label, serializer_cls) in _LIST_SECTIONS.items():
        if key in template and template[key] is not None:
            if not isinstance(template[key], list):
                errors.append(
                    {"section": key, "error": f"Section '{key}' must be a list."}
                )
            else:
                for idx, item in enumerate(template[key]):
                    ser = serializer_cls(data=item)
                    if not ser.is_valid():
                        _collect_errors(label, ser.errors, index=idx)

    return errors
