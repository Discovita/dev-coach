from typing import List
from apps.coach_states.models import CoachState
from apps.identities.models import Identity


def get_identities_context(coach_state: CoachState) -> str:
    """
    Get the user's identities and format them for insertion into a prompt.
    Each identity is formatted into a markdown-compatible string.
    """
    user = coach_state.user
    identities: List[Identity] = user.identities.all()
    formatted_identities = []

    if not identities:
        return "No identities found."

    for identity in identities:
        identity_str = f"### {identity.name} ({identity.get_category_display()}) - {identity.get_state_display()}\n\n"
        if identity.affirmation:
            identity_str += f"**Affirmation:** {identity.affirmation}\n\n"
        if identity.visualization:
            identity_str += f"**Visualization:** {identity.visualization}\n\n"
        if identity.notes:
            notes_str = "\n".join([f"- {note}" for note in identity.notes])
            identity_str += f"**Notes:**\n{notes_str}\n"
        formatted_identities.append(identity_str.strip())

    return "\n\n---\n\n".join(formatted_identities)
