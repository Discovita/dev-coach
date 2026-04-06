"""
create_scenario_user_notes

Create UserNote objects for a test scenario from the template's
``user_notes`` section.
"""

from apps.user_notes.models import UserNote


def create_scenario_user_notes(scenario, template: dict, user) -> None:
    """
    Delete existing scenario user notes, then create fresh ones from the template.

    Args:
        scenario: The TestScenario instance these notes belong to.
        template: The full scenario template dict. Must contain a ``user_notes``
            key with a list of note dicts.
        user: The User instance to assign the notes to.
    """
    UserNote.objects.filter(user=user, test_scenario=scenario).delete()
    for note_data in template["user_notes"]:
        UserNote.objects.create(
            user=user,
            test_scenario=scenario,
            note=note_data.get("note"),
            source_message=None,
            created_at=note_data.get("created_at") or None,
        )
