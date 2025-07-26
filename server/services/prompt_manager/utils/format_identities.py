from typing import List
from apps.identities.models import Identity


def format_identities(identities: List[Identity]) -> str:
    """
    Format a list of Identity objects as markdown-compatible strings.
    """
    if not identities:
        return "No identities found."
    formatted = []
    for identity in identities:
        identity_str = f"#### {identity.name} ({identity.get_category_display()})\n"
        identity_str += f"**ID:** {identity.id}\n"
        if identity.affirmation:
            identity_str += f"**Affirmation:** {identity.affirmation}\n"
        if identity.visualization:
            identity_str += f"**Visualization:** {identity.visualization}\n"
        if identity.notes:
            notes_str = "\n".join([f"- {note}" for note in identity.notes])
            identity_str += f"**Notes:**\n{notes_str}\n"
        formatted.append(identity_str.strip())
    return "\n\n---\n\n".join(formatted)
