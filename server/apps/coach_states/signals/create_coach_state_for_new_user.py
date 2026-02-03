"""
create_coach_state_for_new_user Signal Handler

Auto-creates CoachState when a new User is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.coach_states.models import CoachState
from apps.users.models import User
from enums.coaching_phase import CoachingPhase
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


@receiver(post_save, sender=User)
def create_coach_state_for_new_user(sender, instance, created, **kwargs):
    """
    Auto-create CoachState when a new User is created.

    Steps:
    1. Check if this is a new user (created=True)
    2. If so, create a CoachState with default phase (INTRODUCTION)
    3. Log the creation for traceability

    This ensures every user has a coach state from the moment they are created,
    allowing them to begin coaching sessions immediately.
    """
    if not created:
        return

    CoachState.objects.create(
        user=instance,
        current_phase=CoachingPhase.INTRODUCTION,
    )

    log.debug(f"Created CoachState for user {instance.email}")
