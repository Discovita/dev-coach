"""
Reset all coaching data for a user.

This function deletes all chat messages, identities, user notes, and actions
for a user, resets their coach state, and adds the initial bot message.
"""

from typing import List

from django.db import transaction

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import ensure_initial_message_exists
from apps.coach_states.models import Break, CoachState
from apps.identities.models import Identity
from apps.user_notes.models import UserNote
from apps.users.models import User
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory


@transaction.atomic
def reset_user_coaching_data(user: User) -> List[ChatMessage]:
    """
    Reset all coaching data for a user and return the new chat history.

    This function performs the following operations atomically:
    1. Deletes all chat messages for the user
    2. Deletes all identities for the user
    3. Deletes all user notes for the user
    4. Deletes all actions for the user
    5. Resets the user's CoachState to initial values
    6. Adds the initial bot message

    Args:
        user: The user whose coaching data to reset

    Returns:
        List of ChatMessage objects (the new chat history with initial message)

    Example:
        >>> messages = reset_user_coaching_data(user)
        >>> len(messages)  # Should be 1 (initial message)
        1
    """
    # Delete all chat messages for the user
    ChatMessage.objects.filter(user=user).delete()

    # Delete all identities for the user
    Identity.objects.filter(user=user).delete()

    # Delete all user notes for the user
    UserNote.objects.filter(user=user).delete()

    # Delete all actions for the user
    Action.objects.filter(user=user).delete()

    # Coaching Phase Videos: delete all Break rows so a refreshed user
    # never inherits `on_break=true` from the prior session. Also resets
    # `triggered_by_session` history (not relied on elsewhere, but kept
    # consistent — coaching data should look truly fresh post-reset).
    Break.objects.filter(user=user).delete()

    # Reset the user's CoachState
    try:
        coach_state = CoachState.objects.get(user=user)
        coach_state.current_phase = CoachingPhase.INTRODUCTION
        coach_state.current_identity = None
        coach_state.proposed_identity = None
        coach_state.identity_focus = IdentityCategory.PASSIONS
        coach_state.skipped_identity_categories = []
        coach_state.who_you_are = []
        coach_state.who_you_want_to_be = []
        coach_state.asked_questions = []
        # Coaching Phase Videos: clear acknowledged videos so the welcome
        # card (and every subsequent intro/outro) re-fires on the reset
        # chat — otherwise `transition_phase` / `end_break` would skip
        # them because their keys are still in shown_videos.
        coach_state.shown_videos = []
        coach_state.save()
    except CoachState.DoesNotExist:
        pass  # User may not have a CoachState yet

    # Add the initial bot message
    ensure_initial_message_exists(user)

    # Return the new chat history
    chat_messages = ChatMessage.objects.filter(user=user).order_by("-timestamp")
    return list(chat_messages)
