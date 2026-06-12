"""
Record UserNotes for identity edits/deletes the user makes through the app.

These actions happen OUTSIDE the coaching conversation (on the Identities
pages), so the coaching agent would otherwise have no idea they occurred. We
write a plain-language UserNote so the agent can reference them naturally — the
same channel the Sentinel uses for things it learns in-conversation.
"""

from apps.user_notes.functions.public import create_user_note
from enums.identity_category import IdentityCategory


def _category_label(value):
    """Human-readable category label, falling back to the raw value."""
    try:
        return IdentityCategory(value).label
    except ValueError:
        return str(value)


def capture_identity_fields(identity):
    """Snapshot the user-facing fields we track for edit notes."""
    return {
        "name": identity.name,
        "category": identity.category,
        "i_am_statement": identity.i_am_statement,
    }


def record_identity_edit_note(user, before, identity):
    """
    Create a note describing how ``identity`` changed vs the ``before`` snapshot.

    Only name / category / I Am statement changes are described — scene/image
    fields (clothing, mood, setting) are intentionally ignored since they aren't
    relevant to the coaching conversation. Returns the UserNote, or None when
    no tracked field changed.
    """
    name = identity.name or before.get("name") or "Unnamed"
    changes = []

    if before["name"] != identity.name:
        old_name = before["name"] or "Unnamed"
        changes.append(f'renamed their "{old_name}" identity to "{identity.name}"')

    if before["category"] != identity.category:
        changes.append(
            f'changed the category of their "{name}" identity from '
            f"{_category_label(before['category'])} to "
            f"{_category_label(identity.category)}"
        )

    if before["i_am_statement"] != identity.i_am_statement:
        if identity.i_am_statement:
            changes.append(
                f'updated the I Am statement for their "{name}" identity to: '
                f'"{identity.i_am_statement}"'
            )
        else:
            changes.append(f'cleared the I Am statement for their "{name}" identity')

    if not changes:
        return None

    note = "Outside of our conversation, the user " + "; ".join(changes) + "."
    return create_user_note(user, note, test_scenario=identity.test_scenario)


def record_identity_delete_note(user, identity):
    """Create a note that the user deleted an identity (call before deletion)."""
    name = identity.name or "Unnamed"
    note = f'Outside of our conversation, the user deleted their "{name}" identity.'
    return create_user_note(user, note, test_scenario=identity.test_scenario)
