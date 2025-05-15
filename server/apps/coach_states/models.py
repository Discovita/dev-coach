import uuid
from django.db import models

from apps.identities.models import Identity
from apps.users.models import User

from server.enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from django.contrib.postgres.fields import ArrayField


class CoachState(models.Model):
    """
    Stores the current state of a coaching session for a user.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="coach_state",
        help_text="The user this coach state belongs to.",
    )
    current_state = models.CharField(
        max_length=32,
        choices=CoachingPhase.choices,
        help_text="Current state of the coaching session.",
    )
    current_identity = models.ForeignKey(
        Identity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_coach_states",
        help_text="The identity currently being refined.",
    )
    proposed_identity = models.ForeignKey(
        Identity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="proposed_coach_states",
        help_text="The currently proposed identity.",
    )
    identity_focus = models.CharField(
        max_length=255,
        choices=IdentityCategory.choices,
        default=IdentityCategory.PASSIONS,
        help_text="The identity focus for the coaching session.",
    )
    goals = ArrayField(
        models.CharField(max_length=255),
        default=list,
        null=True,
        blank=True,
        help_text="List of goals for the coaching session. Postgres only.",
    )
    metadata = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Additional metadata for the coaching session.",
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the coach state was last updated."
    )

    def __str__(self):
        return f"CoachState for {self.user.email} ({self.current_state})"
