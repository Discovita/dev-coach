"""
gather_actions_section

Gather all Action objects for a user into a scenario template section list.
"""

from apps.actions.models import Action


def gather_actions_section(user) -> list[dict]:
    """
    Build the ``actions`` template section from the user's live Action records.

    Args:
        user: The User model instance whose actions to capture.

    Returns:
        A list of action dicts. Each dict always contains ``action_type`` and
        ``parameters``. Optional fields (``result_summary``, ``timestamp``,
        ``original_coach_message_id``) are included only when present.
    """
    section: list[dict] = []
    for action in Action.objects.filter(user=user).order_by("timestamp"):
        entry: dict = {
            "action_type": action.action_type,
            "parameters": action.parameters,
        }
        if action.result_summary:
            entry["result_summary"] = action.result_summary
        if action.timestamp:
            entry["timestamp"] = action.timestamp.isoformat()
        if action.coach_message:
            entry["original_coach_message_id"] = str(action.coach_message.id)
        section.append(entry)
    return section
