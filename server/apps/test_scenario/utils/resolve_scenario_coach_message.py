"""
resolve_scenario_coach_message

Find the ChatMessage to link an Action to during scenario instantiation.
"""

from apps.chat_messages.models import ChatMessage


def resolve_scenario_coach_message(
    action_data: dict,
    template: dict,
    user,
    scenario,
    original_to_new_msg: dict,
):
    """
    Find the ChatMessage to link an Action to.

    Resolution strategy (in priority order):
    1. ID-based mapping via ``original_coach_message_id`` and
       ``original_message_mapping`` — preferred, most accurate.
    2. Content-based matching via ``coach_message_content`` — deprecated
       fallback for older templates.
    3. Most recent coach message — last-resort fallback.

    Args:
        action_data: A single action dict from the template.
        template: The full scenario template dict, which may contain
            ``original_message_mapping``.
        user: The User instance the messages belong to.
        scenario: The TestScenario instance the messages belong to.
        original_to_new_msg: Mapping of ``"role|content|timestamp"`` keys to
            the newly created ChatMessage instances.

    Returns:
        The matched ChatMessage instance, or the most recent coach message
        as a fallback, or ``None`` if no coach message exists.
    """

    def fallback():
        return (
            ChatMessage.objects.filter(user=user, test_scenario=scenario, role="coach")
            .order_by("-timestamp")
            .first()
        )

    # ID-based mapping (preferred)
    if action_data.get("original_coach_message_id") and template.get(
        "original_message_mapping"
    ):
        original_msg_data = template["original_message_mapping"].get(
            action_data["original_coach_message_id"]
        )
        if original_msg_data:
            key = (
                f"{original_msg_data.get('role')}|{original_msg_data.get('content')}"
                f"|{original_msg_data.get('timestamp', '')}"
            )
            msg = original_to_new_msg.get(key)
            if msg:
                return msg
        return fallback()

    # Content-based matching (deprecated)
    if action_data.get("coach_message_content"):
        qs = ChatMessage.objects.filter(
            user=user,
            test_scenario=scenario,
            role="coach",
            content=action_data["coach_message_content"],
        ).order_by("-timestamp")
        if qs.exists():
            return qs.first()
        return fallback()

    return fallback()
