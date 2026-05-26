"""
create_scenario_breaks

Create Break objects for a test scenario from the template's ``breaks``
section, linking each break to its originating SESSION_BREAK coach
message.

Part of the Coaching Phase Videos freeze/instantiate pipeline. Mirrors
``create_scenario_actions``: deletes any existing rows for this user,
then recreates from the template. The ``coach_message`` FK is resolved
via ``resolve_scenario_coach_message`` (same helper Actions use — it
just reads ``entry["original_coach_message_id"]`` against
``template["original_message_mapping"]``).
"""

from apps.coach_states.models import Break
from apps.test_scenario.utils.resolve_scenario_coach_message import (
    resolve_scenario_coach_message,
)


def create_scenario_breaks(
    scenario, template: dict, user, original_to_new_msg: dict
) -> None:
    """
    Delete the user's existing Break rows, then create fresh ones from
    the template.

    The Break model has no ``test_scenario`` FK (unlike Action / UserNote
    / ChatMessage), but scenario users are deleted-and-recreated by
    ``create_scenario_user``, so a per-user delete is sufficient AND
    symmetric with the broader pipeline's "clear before recreate" idiom.

    Args:
        scenario: The TestScenario instance these breaks belong to.
        template: The full scenario template dict. Must contain a
            ``breaks`` key with a list of break dicts.
        user: The User instance to assign the breaks to.
        original_to_new_msg: Mapping of ``"role|content|timestamp"`` keys
            to newly created ChatMessage instances (from
            ``create_scenario_chat_messages``).
    """
    Break.objects.filter(user=user).delete()

    for break_data in template["breaks"]:
        coach_message = resolve_scenario_coach_message(
            break_data, template, user, scenario, original_to_new_msg
        )
        br = Break.objects.create(
            user=user,
            triggered_by_session=break_data.get("triggered_by_session", ""),
            ended_at=break_data.get("ended_at") or None,
            coach_message=coach_message,
        )
        # `started_at` is `auto_now_add=True` on the model — the value
        # passed to `create()` would be ignored. Use `.update()` to bypass
        # auto_now_add and preserve the captured timestamp so frozen
        # break durations stay meaningful.
        started_at = break_data.get("started_at")
        if started_at:
            Break.objects.filter(id=br.id).update(started_at=started_at)
