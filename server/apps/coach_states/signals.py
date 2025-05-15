from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from apps.coach_states.models import CoachState
from enums.coaching_phase import CoachingPhase


@receiver(post_save, sender=User)
def create_coach_state_for_new_user(sender, instance, created, **kwargs):
    """
    Signal to create a CoachState for every new user.
    """
    if created:
        CoachState.objects.create(
            user=instance, current_state=CoachingPhase.INTRODUCTION
        )
