from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_category import IdentityCategory


def get_identities_context(coach_state: CoachState) -> str:
    """
    Get the user's identities and format them for insertion into a prompt.
    Each identity is formatted into a markdown-compatible string.
    Also includes a section listing skipped identity categories (if any).
    """
    user = coach_state.user
    identities: List[Identity] = user.identities.all()
    formatted_identities = []

    # Step 1: Format skipped identity categories (if any)
    skipped = coach_state.skipped_identity_categories or []
    skipped_section = ""
    if skipped:
        # Convert each skipped category to its display label
        skipped_labels = []
        for cat in skipped:
            try:
                skipped_labels.append(IdentityCategory.from_string(cat).label)
            except Exception:
                skipped_labels.append(str(cat))  # fallback to raw value
        skipped_section = (
            "\n\n---\n\n" + 
            "**Skipped Identity Categories:**\n" +
            "\n".join([f"- {label}" for label in skipped_labels])
        )

    # Step 2: Format identities as before
    if not identities:
        return (skipped_section or "") + "No identities found."

    for identity in identities:
        identity_str = f"#### {identity.name} ({identity.get_category_display()}) - {identity.get_state_display()}\n"
        if identity.affirmation:
            identity_str += f"**Affirmation:** {identity.affirmation}\n"
        if identity.visualization:
            identity_str += f"**Visualization:** {identity.visualization}\n"
        if identity.notes:
            notes_str = "\n".join([f"- {note}" for note in identity.notes])
            identity_str += f"**Notes:**\n{notes_str}\n"
        formatted_identities.append(identity_str.strip())

    return "\n\n---\n\n".join(formatted_identities) + (skipped_section or "")
