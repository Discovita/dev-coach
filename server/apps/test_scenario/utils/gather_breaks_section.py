"""
gather_breaks_section

Gather all Break objects for a user into a scenario template section list.

Part of the Coaching Phase Videos freeze/instantiate pipeline. Mirrors
the actions/user_notes pattern: serialize each row, capture the
``coach_message`` FK via its original UUID so the create side can resolve
it against the just-created ChatMessages.
"""

from apps.coach_states.models import Break


def gather_breaks_section(user) -> list[dict]:
    """
    Build the ``breaks`` template section from the user's live Break records.

    Args:
        user: The User model instance whose breaks to capture.

    Returns:
        A list of break dicts, oldest first. Each dict always contains
        ``triggered_by_session``. Optional fields (``started_at``,
        ``ended_at``, ``original_coach_message_id``) are included only
        when present.
    """
    section: list[dict] = []
    for br in Break.objects.filter(user=user).order_by("started_at"):
        entry: dict = {"triggered_by_session": br.triggered_by_session}
        if br.started_at:
            entry["started_at"] = br.started_at.isoformat()
        if br.ended_at:
            entry["ended_at"] = br.ended_at.isoformat()
        if br.coach_message_id:
            entry["original_coach_message_id"] = str(br.coach_message_id)
        section.append(entry)
    return section
