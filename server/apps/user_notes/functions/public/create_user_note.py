"""
Create a single UserNote.

A small public helper so other apps (e.g. identity edit/delete endpoints) can
record a note about something the user did, without each caller reaching into
the ORM directly. Notes created here feed the coaching agent's prompt via
`get_user_notes_context`.
"""

from apps.user_notes.models import UserNote


def create_user_note(user, note, *, test_scenario=None, source_message=None):
    """
    Create a UserNote for ``user``.

    Args:
        user: The user the note is about.
        note: The note text. Blank/whitespace-only notes are ignored.
        test_scenario: Optional TestScenario for test-data isolation (e.g. when
            an admin acts on an impersonated test user's identity).
        source_message: Optional ChatMessage that prompted the note.

    Returns:
        The created UserNote, or None if the note text was blank.
    """
    text = (note or "").strip()
    if not text:
        return None

    return UserNote.objects.create(
        user=user,
        note=text,
        test_scenario=test_scenario,
        source_message=source_message,
    )
