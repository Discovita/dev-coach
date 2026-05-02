"""
gather_user_notes_section

Gather all UserNote objects for a user into a scenario template section list.
"""

from apps.user_notes.models import UserNote


def gather_user_notes_section(user) -> list[dict]:
    """
    Build the ``user_notes`` template section from the user's live UserNote records.

    Args:
        user: The User model instance whose notes to capture.

    Returns:
        A list of note dicts. Each dict always contains ``note``. Optional
        fields (``source_message``, ``created_at``) are included only when
        present.
    """
    section: list[dict] = []
    for note in UserNote.objects.filter(user=user):
        entry: dict = {"note": note.note}
        if note.source_message:
            entry["source_message"] = str(note.source_message.id)
        if note.created_at:
            entry["created_at"] = note.created_at.isoformat()
        section.append(entry)
    return section
