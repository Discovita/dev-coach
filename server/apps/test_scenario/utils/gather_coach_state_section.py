"""
gather_coach_state_section

Gather the CoachState for a user into a scenario template section dict.
"""

from apps.coach_states.models import CoachState


def gather_coach_state_section(user) -> dict | None:
    """
    Build the ``coach_state`` template section from the user's live CoachState.

    Args:
        user: The User model instance whose CoachState to capture.

    Returns:
        A dict with all CoachState fields relevant to the template, or
        ``None`` if the user has no CoachState.
    """
    try:
        cs = CoachState.objects.get(user=user)
    except CoachState.DoesNotExist:
        return None

    section: dict = {
        "current_phase": cs.current_phase,
        "identity_focus": cs.identity_focus,
        "who_you_are": cs.who_you_are,
        "who_you_want_to_be": cs.who_you_want_to_be,
    }
    if getattr(cs, "skipped_identity_categories", None):
        section["skipped_identity_categories"] = cs.skipped_identity_categories
    if getattr(cs, "current_identity", None):
        section["current_identity"] = str(cs.current_identity.id)
    if getattr(cs, "proposed_identity", None):
        section["proposed_identity"] = str(cs.proposed_identity.id)
    if getattr(cs, "asked_questions", None):
        section["asked_questions"] = cs.asked_questions
    if getattr(cs, "metadata", None):
        section["metadata"] = cs.metadata
    # Coaching Phase Videos: capture acknowledged video keys so a frozen
    # scenario replays with the correct intro/outro cards still pending
    # (or skipped) for the user's current_phase.
    if getattr(cs, "shown_videos", None):
        section["shown_videos"] = cs.shown_videos
    return section
