"""
gather_chat_messages_section

Gather all ChatMessage objects for a user into a scenario template section list.
"""

from apps.chat_messages.models import ChatMessage


def gather_chat_messages_section(user) -> tuple[list[dict], dict]:
    """
    Build the ``chat_messages`` template section and an ID-keyed mapping dict.

    The mapping dict (``original_message_mapping``) is used during
    instantiation to link Action objects back to their originating coach
    messages by content/timestamp key, enabling robust re-linking even after
    IDs change.

    Args:
        user: The User model instance whose messages to capture.

    Returns:
        A 2-tuple of:
        - ``section``: List of message dicts (role, content, optional timestamp
          and component_config).
        - ``mapping``: Dict keyed by original message UUID string, mapping to
          the same fields for later cross-referencing.
    """
    section: list[dict] = []
    mapping: dict = {}
    for msg in ChatMessage.objects.filter(user=user).order_by("timestamp"):
        entry: dict = {"role": msg.role, "content": msg.content}
        if msg.timestamp:
            entry["timestamp"] = msg.timestamp.isoformat()
        if msg.component_config:
            entry["component_config"] = msg.component_config
        section.append(entry)
        mapping[str(msg.id)] = {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            "component_config": msg.component_config,
        }
    return section, mapping
