import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Max

from apps.core.models import ImageMixin
from apps.users.models import User
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState


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
    clothing = models.TextField(
        null=True,
        blank=True,
        help_text="What the person is wearing in this identity visualization (e.g., 'linen button-down shirt')",
    )
    mood = models.TextField(
        null=True,
        blank=True,
        help_text="Emotional state/feeling in this identity visualization (e.g., 'proud and calm')",
    )
    setting = models.TextField(
        null=True,
        blank=True,
        help_text="Environment/location for this identity visualization (e.g., 'on a hill overlooking the ocean')",
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
    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text=(
            "User-controlled display order (ascending). New identities are "
            "appended to the end; ties break on created_at."
        ),
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

    def save(self, *args, **kwargs):
        """
        On creation, append the identity to the end of the user's order
        (max existing order + 1) unless an explicit order was provided.
        This preserves "earliest created first" as the default ordering.
        """
        if self._state.adding and self.order == 0:
            max_order = Identity.objects.filter(user_id=self.user_id).aggregate(
                max_order=Max("order")
            )["max_order"]
            self.order = 0 if max_order is None else max_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the identity for admin/debugging.
        """
        return f"{self.name[:30]} ({self.get_category_display()}) - {self.get_state_display()}"

    class Meta:
        verbose_name = "Identity"
        verbose_name_plural = "Identities"
        ordering = ["order", "created_at"]
