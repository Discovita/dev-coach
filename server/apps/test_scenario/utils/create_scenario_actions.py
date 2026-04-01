"""
create_scenario_actions

Create Action objects for a test scenario from the template's ``actions``
section, linking each action to its originating coach message.
"""

from apps.actions.models import Action
from apps.test_scenario.utils.resolve_scenario_coach_message import (
    resolve_scenario_coach_message,
)


def create_scenario_actions(
    scenario, template: dict, user, original_to_new_msg: dict
) -> None:
    """
    Delete existing scenario actions, then create fresh ones from the template.

    Each action is linked to its originating coach ChatMessage via
    ``resolve_scenario_coach_message``.

    Args:
        scenario: The TestScenario instance these actions belong to.
        template: The full scenario template dict. Must contain an ``actions``
            key with a list of action dicts.
        user: The User instance to assign the actions to.
        original_to_new_msg: Mapping of ``"role|content|timestamp"`` keys to
            newly created ChatMessage instances (from
            ``create_scenario_chat_messages``).
    """
    Action.objects.filter(user=user, test_scenario=scenario).delete()

    for action_data in template["actions"]:
        coach_message = resolve_scenario_coach_message(
            action_data, template, user, scenario, original_to_new_msg
        )
        Action(
            user=user,
            test_scenario=scenario,
            action_type=action_data.get("action_type"),
            parameters=action_data.get("parameters", {}),
            result_summary=action_data.get("result_summary", ""),
            timestamp=action_data.get("timestamp") or None,
            coach_message=coach_message,
        ).save()
