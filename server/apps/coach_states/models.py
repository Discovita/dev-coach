import uuid
from django.db import models

from apps.identities.models import Identity
from apps.users.models import User

from enums.coaching_phase import CoachingPhase
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
    current_phase = models.CharField(
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
        help_text="The Identity currently being refined in the Identity Refinement Phase",
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
        help_text="The identity category focus for the coaching session. Used when ",
    )
    skipped_identity_categories = ArrayField(
        models.CharField(max_length=64, choices=IdentityCategory.choices),
        default=list,
        blank=True,
        help_text="List of identity categories that the user has chosen to skip.",
    )
    who_you_are = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="List of 'who you are' identities provided by the user.",
    )
    who_you_want_to_be = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="List of 'who you want to be' identities provided by the user.",
    )
    asked_questions = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="List of questions that have been asked during the Get To Know You phase.",
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
    test_scenario = models.ForeignKey(
        'test_scenario.TestScenario',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Test scenario this coach state is associated with (for test data isolation)."
    )

    def __str__(self):
        return f"CoachState for {self.user.email} ({self.current_phase})"
