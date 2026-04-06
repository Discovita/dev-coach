"""
create_scenario_chat_messages

Create ChatMessage objects for a test scenario from the template's
``chat_messages`` section.
"""

from apps.chat_messages.models import ChatMessage


def create_scenario_chat_messages(scenario, template: dict, user) -> dict:
    """
    Delete existing scenario chat messages, then create fresh ones from the template.

    Returns a content-keyed mapping used by ``create_scenario_actions`` to
    re-link actions to their originating coach messages after IDs change.

    Args:
        scenario: The TestScenario instance these messages belong to.
        template: The full scenario template dict. Must contain a
            ``chat_messages`` key with a list of message dicts.
        user: The User instance to assign the messages to.

    Returns:
        A dict mapping ``"role|content|timestamp"`` keys to ChatMessage
        instances, for use in ``create_scenario_actions``.
    """
    ChatMessage.objects.filter(user=user, test_scenario=scenario).delete()
    mapping: dict[str, ChatMessage] = {}

    for msg_data in template["chat_messages"]:
        msg = ChatMessage.objects.create(
            user=user,
            test_scenario=scenario,
            role=msg_data.get("role"),
            content=msg_data.get("content"),
            timestamp=msg_data.get("timestamp") or None,
            component_config=msg_data.get("component_config"),
        )
        key = (
            f"{msg_data.get('role')}|{msg_data.get('content')}"
            f"|{msg_data.get('timestamp', '')}"
        )
        mapping[key] = msg

    return mapping
