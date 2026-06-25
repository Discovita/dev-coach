import uuid

from django.db import models

from apps.users.models import User
from enums.meditation import MeditationStatus


class Meditation(models.Model):
    """
    One meditation run for a user — the lifecycle container for a set of
    per-identity segments that an admin generates, QCs, and (later) assembles
    into a final video.

    "Pending" is a status, not a separate table: the admin table filters on
    ``status``.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="meditations",
        help_text="The user this meditation is for",
    )
    status = models.CharField(
        max_length=32,
        choices=MeditationStatus.choices,
        default=MeditationStatus.PENDING,
    )
    final_video_s3_key = models.CharField(
        max_length=1024,
        blank=True,
        default="",
        help_text="S3 key of the assembled final video (set in Phase 4 assembly)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Meditation for {self.user.email} ({self.status})"
