from apps.coach_states.models import CoachState
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def get_current_identity_context(coach_state: CoachState) -> str:
    """
    Get the current identity being refined in the Identity Refinement Phase.
    Returns the name of the current identity if one is set, otherwise returns None.
    """
    identity = coach_state.current_identity
    log.debug(f"Current Identity: {identity.name}")
    if identity:
        current_identity_str = f"#### {identity.name}\n"
        current_identity_str += f"**ID:** {identity.id}\n"
        current_identity_str += (
            f"**State:** {identity.state if identity.state else 'None'}\n"
        )
        current_identity_str += (
            f"**Category:** {identity.category if identity.category else 'None'}\n"
        )
        if identity.notes:
            notes_str = "\n".join([f"- {note}" for note in identity.notes])
            current_identity_str += f"**Notes:**\n{notes_str}\n"
        return current_identity_str
    else:
        return "No current identity set."