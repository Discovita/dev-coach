import uuid

from django.db import models
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState
from apps.users.models import User
from django.contrib.postgres.fields import ArrayField
from apps.core.models import ImageMixin


# The Identity model stores a single identity for a user, including its state, notes, and category.
# This model is used in the coaching system to track user identities and their progress.
# Referenced in: CoachState, coaching logic, admin, and API serializers.
class Identity(ImageMixin, models.Model):
    """
    Represents a single identity with its state for a user in the coaching system.
    """

    # NOTE: Image field inherited from ImageMixin (VersatileImageField with UUID-based paths)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="identities",
        help_text="The user this identity belongs to.",
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="A concise label for the identity (e.g., 'Creative Visionary')",
    )
    i_am_statement = models.TextField(
        help_text="An 'I am' statement with a brief description",
        null=True,
        blank=True,
    )
    visualization = models.TextField(
        help_text="(Added in the visualization stage) A vivid mental image",
        null=True,
        blank=True,
    )
    state = models.CharField(
        max_length=32,
        choices=IdentityState.choices,
        default=IdentityState.PROPOSED,
        help_text="Current state of the identity (proposed, accepted, refinement complete).",
        null=True,
        blank=True,
    )
    notes = ArrayField(
        models.TextField(),
        default=list,
        help_text="List of notes about the identity.",
        blank=True,
    )
    category = models.CharField(
        max_length=32,
        choices=IdentityCategory.choices,
        help_text="Category this identity belongs to.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the identity was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the identity was last updated."
    )
    test_scenario = models.ForeignKey(
        "test_scenario.TestScenario",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Test scenario this identity is associated with (for test data isolation).",
    )

    def __str__(self):
        """
        String representation of the identity for admin/debugging.
        """
        return f"{self.name[:30]} ({self.get_category_display()}) - {self.get_state_display()}"

    class Meta:
        verbose_name = "Identity"
        verbose_name_plural = "Identities"
