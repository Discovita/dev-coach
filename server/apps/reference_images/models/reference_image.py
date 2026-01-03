import uuid
from django.db import models
from apps.users.models import User
from apps.core.models import ImageMixin


class ReferenceImage(ImageMixin, models.Model):
    """
    Reference images uploaded by/for a user for AI image generation.
    Each user can have up to 5 reference images.
    These are used as input to Gemini for generating identity images.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reference_images",
        help_text="The user these reference images belong to",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional name/label for this image (e.g., 'Headshot 1')",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (0-4)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "order"], name="unique_user_image_order"
            )
        ]

    def __str__(self):
        return f"{self.user.email} - Reference Image {self.order + 1}"

